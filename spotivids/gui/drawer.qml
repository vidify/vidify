import QtQuick 2.13
import QtQuick.Controls 2.13

Drawer {
    id: drawer
    width: 0.66 * window.width
    height: window.height

    Label {
        text: "Content goes here!"
        anchors.centerIn: parent
    }
}
