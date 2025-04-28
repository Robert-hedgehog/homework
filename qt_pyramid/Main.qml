import QtQuick

Window {
    width: 600
    height: 600
    visible: true
    title: qsTr("Pyramid")

    // Нижний ряд: 3 кубика
    My_Comp {
        width: 100
        height: 100
        id: bottomcenter
        anchors.centerIn: parent
        comColor: "blue"
    }

    My_Comp {
        width: 100
        height: 100
        id: bottomright
        anchors.left: bottomcenter.right
        anchors.top: bottomcenter.top
        anchors.leftMargin: 10
        comColor: "blue"
    }

    My_Comp {
        width: 100
        height: 100
        id: bottomleft
        anchors.right: bottomcenter.left
        anchors.top: bottomcenter.top
        anchors.rightMargin: 10
        comColor: "blue"
    }

    // Средний ряд: 2 кубика
    My_Comp {
        width: 100
        height: 100
        id: centerleft
        anchors.horizontalCenter: bottomcenter.horizontalCenter
        anchors.horizontalCenterOffset: -55
        anchors.bottom: bottomcenter.top
        anchors.bottomMargin: 10
        comColor: "green"
    }

    My_Comp {
        width: 100
        height: 100
        id: centerright
        anchors.horizontalCenter: bottomcenter.horizontalCenter
        anchors.horizontalCenterOffset: 55
        anchors.bottom: bottomcenter.top
        anchors.bottomMargin: 10
        comColor: "green"
    }

    // Верхний ряд: 1 кубика
    My_Comp {
        width: 100
        height: 100
        id: topcenter
        anchors.horizontalCenter: bottomcenter.horizontalCenter
        anchors.bottom: bottomcenter.top
        anchors.bottomMargin: 120
        comColor: "red"
    }
}
