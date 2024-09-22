docker build -t iphone_bark:latest .

docker run -d --restart always --name="iphone_bark" -e bk="pSMSJbQYRgQD6BTrkxCp9D" iphone_bark:latest