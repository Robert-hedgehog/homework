function doGet(e) {
  return HtmlService.createHtmlOutputFromFile('index')
      .setXFrameOptionsMode(HtmlService.XFrameOptionsMode.ALLOWALL);
}

// Вспомогательная функция для получения или создания папки
function getOrCreateFolder(baseFolder, folderName) {
  const folders = baseFolder.getFoldersByName(folderName);
  if (folders.hasNext()) {
    return folders.next();
  } else {
    Logger.log('Создаю папку: ' + folderName + ' внутри ' + baseFolder.getName());
    return baseFolder.createFolder(folderName);
  }
}

// Основная функция, которую будет вызывать HTML-форма
function processFormData(formData, filesData) {
  try {
    Logger.log('Получены данные формы: ' + JSON.stringify(formData));
    // Добавим проверку и инициализацию filesData, если оно не передано корректно
    if (filesData && typeof filesData.length !== 'undefined') {
        Logger.log('Получено файлов: ' + filesData.length);
    } else {
        Logger.log('Данные о файлах не получены или некорректны. filesData будет пустым массивом.');
        filesData = []; // Инициализируем как пустой массив, чтобы избежать ошибок далее
    }

    const ss = SpreadsheetApp.getActiveSpreadsheet();
    const sheet2 = ss.getSheetByName('Комментарии');

    // Проверяем, найдены ли листы
    if (!sheet2) {
      Logger.log('Ошибка: Лист "Комментарии" не найден в таблице.');
      return 'Ошибка: Лист "Комментарии" не найден в таблице.';
    }

    const placeName = formData.placeName || 'Без названия';
    const comment = formData.comment || '';
    const reaction = formData.reaction || 'не указана';

    /* Генерируем ID. Это будет номер следующей строки листа "Комментарии".
    Он также будет использоваться как имя папки и как ID для записи в таблицы.
    Преобразуем в строку, так как имя папки должно быть строкой. */
    const generatedId = (sheet2.getLastRow()).toString();

    // Работа с Google Drive
    const spreadsheetFile = DriveApp.getFileById(ss.getId());
    let projectFolder; // Папка, в которой находится текущая таблица
    const parents = spreadsheetFile.getParents();
    if (parents.hasNext()) {
        projectFolder = parents.next();
    }

    const photosRootFolder = getOrCreateFolder(projectFolder, 'Photos');
    // Папка с именем generatedId внутри "Photos"
    const specificPhotoFolder = getOrCreateFolder(photosRootFolder, generatedId);

    let photosFolderUrl = specificPhotoFolder.getUrl(); // URL этой папки

    // Загружаем фотографии, если они есть
    if (filesData && filesData.length > 0) {
      Logger.log('Начинаю загрузку ' + filesData.length + ' файлов в папку: ' + specificPhotoFolder.getName());
      for (let i = 0; i < filesData.length; i++) {
        const file = filesData[i];
        // Добавим проверку, что все необходимые данные для файла есть
        if (file && typeof file.base64Content !== 'undefined' && typeof file.mimeType !== 'undefined' && typeof file.fileName !== 'undefined') {
            const decoded = Utilities.base64Decode(file.base64Content);
            const blob = Utilities.newBlob(decoded, file.mimeType, file.fileName);
            // Файлы сохраняются в specificPhotoFolder
            const savedFile = specificPhotoFolder.createFile(blob);
            Logger.log('Файл сохранен: ' + savedFile.getName() + ' в папку ' + specificPhotoFolder.getName());
        } else {
            Logger.log('Пропущен некорректный файловый объект под индексом ' + i + ': ' + JSON.stringify(file));
        }
      }
    } else {
      Logger.log('Фотографии не были прикреплены или массив filesData пуст.');
    }

    // Запись данных в таблицу
    sheet2.appendRow([generatedId, placeName, comment, reaction, photosFolderUrl]);
    Logger.log('Запись на Лист2 ("Комментарии"): ID=' + generatedId +
               ', Название="' + placeName +
               '", Комментарий="' + comment +
               '", Реакция="' + reaction +
               '", Ссылка фото="' + photosFolderUrl + '"');

  } catch (error) {
    // Детальное логирование ошибки на стороне сервера
    let errorMessage = error.toString();
    if (error.message && error.fileName && error.lineNumber) {
        errorMessage = `Ошибка: ${error.message} в файле ${error.fileName}, строка ${error.lineNumber}. Stack: ${error.stack}`;
    }
    Logger.log('Критическая ошибка в processFormData: ' + errorMessage);
    return 'Произошла ошибка при обработке данных: ' + error.toString();
  }
}