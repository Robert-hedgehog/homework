import QtQuick

Window {
    width: 400
    height: 700
    visible: true
    title: qsTr("Model on anchors")

    Item {
        id: root
        anchors.fill: parent
        Rectangle {
            id:header
            height: parent.height * 0.1
            color: "#dcdcdc"
            anchors.top: parent.top
            anchors.left: parent.left
            anchors.right:parent.right
            Text {
                text: "Header"
                anchors.centerIn: header
            }
        }
        Rectangle {
            id:content
            border.color: "#dcdcdc"
            border.width: 2
            anchors.top: header.bottom
            anchors.left: parent.left
            anchors.right: parent.right
            anchors.bottom: footer.top
            anchors.margins:10
            Text {
                text: "Content"
                anchors.centerIn: content
            }
        }
        Rectangle {
            id:footer
            anchors.left: parent.left
            anchors.right: parent.right
            anchors.bottom: parent.bottom
            height: parent.height * 0.1
            color: "#dcdcdc"

            Row {
                anchors.fill: parent
                spacing: 10

                Rectangle {
                    color: "#d3d3d3"
                    border.color: "#c9c9c9"
                    width: (parent.width - 2 * parent.spacing) / 3
                    height: parent.height

                    Text {
                        text: "1"
                        anchors.centerIn: parent
                    }
                }
                Rectangle {
                    color: "#d3d3d3"
                    border.color: "#c9c9c9"
                    width: (parent.width - 2 * parent.spacing) / 3
                    height: parent.height

                    Text {
                        text: "2"
                        anchors.centerIn: parent
                    }
                }
                Rectangle {
                    color: "#d3d3d3"
                    border.color: "#c9c9c9"
                    width: (parent.width - 2 * parent.spacing) / 3
                    height: parent.height

                    Text {
                        text: "3"
                        anchors.centerIn: parent
                    }
                }
            }
        }
    }
}
