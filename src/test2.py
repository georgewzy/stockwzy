import sys
from PyQt5.QtWidgets import *
from functools import partial
class WinForm(QMainWindow):
  def __init__(self,parent=None):
    super(WinForm, self).__init__(parent)
    #实例化两个按钮
    button1=QPushButton('Button1')
    button2=QPushButton('Button2')
    #todo 第一种方法
    #单击信号关联槽函数，利用Lanbda表达式传递一个参数
    # button1.clicked.connect(lambda :self.onButtonClick(1))
    # button2.clicked.connect(lambda :self.onButtonClick(2))
    #
    #todo 第二种方法
    button1.clicked.connect(partial(self.onButtonClick, 1))
    button2.clicked.connect(partial(self.onButtonClick, 2))
    #实例化窗口
    main=QWidget()
    #设置窗口的布局，并向其中添加控件
    layout=QHBoxLayout(main)
    layout.addWidget(button1)
    layout.addWidget(button2)
    #设置为中央控件
    self.setCentralWidget(main)
  def onButtonClick( self,n ):
    #弹窗信息提示框，输出被点击的信息
    print("Button {0}".format(n))
    QMessageBox.information(self,'信息提示框','Button {0}'.format(n))
if __name__ == '__main__':
  app=QApplication(sys.argv)
  form=WinForm()
  form.show()
  sys.exit(app.exec_())