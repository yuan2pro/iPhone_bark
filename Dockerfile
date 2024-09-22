FROM python:3.11-slim
RUN ["pip", "install", "requests"]
ENV TZ=Asia/Shanghai
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone
ADD iPhone_bark.py /

USER root
# 传递参数
ENV xh="MYTQ3CH/A"
ENV dq="广东-深圳-南山区"
ENV bk="ELvJ9NHnM7cqvUtuyeS8c6"
ENV bs="https://api.day.app/"
ENV mz=""
ENV ys=""
ENV rl=""
ENV cs="深圳,广州"
ENV dp=""
ENV qdsj="2024-09-15 20:00:00"
ENV tzsj="2024-10-01 00:00:00"
ENV bark="1"
ENV wxpush="0"
ENV wxpushtoken="AT_uhjpnxvzuzqWRJj9YsDrqdFJwpCxa38L"
ENV wxpushuids=""
ENV wxpushtopicIds="12489" 

CMD python /iPhone_bark.py -xh=$xh -dq=$dq -bk=$bk -bs=$bs -mz=$mz -ys=$ys -rl=$rl -cs=$cs -dp=$dp -qdsj="$qdsj" -tzsj="$tzsj" -bark=$bark -wxpush=$wxpush -wxpushtoken=$wxpushtoken -wxpushuids=$wxpushuids -wxpushtopicIds=$wxpushtopicIds

