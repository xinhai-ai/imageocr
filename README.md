# imageocr
openwebui函数，在交给模型处理前对传入的图片进行文字识别

# 使用方法
复制[imageocr.py](https://github.com/xinhai-ai/imageocr/blob/main/imageocr.py)的内容

前往**管理员设置**界面

![image](https://github.com/user-attachments/assets/03a9a144-a6b2-4897-a834-8c2d966468cd)


**点击添加函数**

![image](https://github.com/user-attachments/assets/5d29dadb-73b3-4a93-a0f0-6fa91180bd86)
![image](https://github.com/user-attachments/assets/56da0012-0bad-4b11-a561-6541ffc2b0a6)
![image](https://github.com/user-attachments/assets/efa063d4-d22d-415c-9d22-9f5955892a2b)



在工作空间新建一个模型

![image](https://github.com/user-attachments/assets/f1f01135-a9a8-40dd-aa22-855782685af5)


## 注意

**只能在首轮对话时传入一张图片**

只有在首轮对话时才会进行文字识别，在之后的对话中，会**将传入的图片剔除**


# 特别感谢
https://linux.do/t/topic/259708 修改自此函数
