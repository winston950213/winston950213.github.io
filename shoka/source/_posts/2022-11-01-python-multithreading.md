---
title: python多线程学习
date: '2022-11-01T00:53:01+08:00'
permalink: 2022/11/01/python多线程学习/
categories:
- 编程语言
tags:
- python
- 多线程
comment: false
fancybox: true
---

python 多线程一点研究,有待深入

<!-- more -->

#### 线程模块

在 Python3 通过两个标准库 _thread 和 threading 提供对线程的支持。

- _thread 提供了低级别的、原始的线程以及一个简单的锁
- threading 对_thread 进行封装并且扩展了功能，所以现在基本上 python 多线程都使用 threading

#### 创建线程

1. 方法一:
   

```python
# 使用函数的方式创建
 import threading
 import time

 def func(arg):
     time.sleep(1)
     print('thread '+str(arg)+" running....")

 if __name__ == '__main__':
     for i in range(10):
         t = threading.Thread(target=func, args=(i,))
         t.start()
```
2. 方法二:
   

```python
# 使用继承Thread类的方式创建
import threading

class MyThread(threading.Thread):
    def __init__(self, thread_name):
        # 注意：一定要显式的调用父类的初始化函数。
        super(MyThread, self).__init__(name=thread_name)

    def run(self):
        print("%s正在运行中......" % self.name)

if __name__ == '__main__':
    for i in range(10):
        MyThread("thread-" + str(i)).start() #此行代码也可分开写,先创建MyThread对象,在调用start方法
```

#### 疑惑

1. `start` 和 `join` 干了什么？

   `ctrl` + 左键点击进去 start 源码看到注释:
   

```python
"""Start the thread's activity.

    It must be called at most once per thread object. It arranges for the
    object's run() method to be invoked in a separate thread of control.

    This method will raise a RuntimeError if called more than once on the
    same thread object.
"""
```

   简单来说就是激活一个线程，在 run () 方法之后被独立调用，重复调用会抛出 `RuntimeError`
   

```python
"""Wait until the thread terminates.

    This blocks the calling thread until the thread whose join() method is
    called terminates -- either normally or through an unhandled exception
    or until the optional timeout occurs.

    When the timeout argument is present and not None, it should be a
    floating point number specifying a timeout for the operation in seconds
    (or fractions thereof). As join() always returns None, you must call
    is_alive() after join() to decide whether a timeout happened -- if the
    thread is still alive, the join() call timed out.

    When the timeout argument is not present or None, the operation will
    block until the thread terminates.

    A thread can be join()ed many times.

    join() raises a RuntimeError if an attempt is made to join the current
    thread as that would cause a deadlock. It is also an error to join() a
    thread before it has been started and attempts to do so raises the same
    exception.
    """
```

   join () 会一直等待知道所有线程结束
   就方法一中的代码如果直接在 for 循环中加入 join 的话会导致执行时间为 10s

   正确做法:
   

```python
import threading
import time

def func(arg):
    time.sleep(1)
    print('thread '+str(arg)+" running....")

if __name__ == '__main__':
    start = time.time()
    threads = []
    for i in range(10):
        t = threading.Thread(target=func, args=(i,))
        threads.append(t)
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    print(time.time() - start)
```
2. 同时写入多个文件
   

```python
import threading
import time

def func_fs(name):
    with open(f"{name}.txt", "w") as target:
        time.sleep(5) # 假装写入很久
        target.write("这是一段很长的文本")

if __name__ == "__main__":
    start = time.time()
    l_thread = []
    for i in range(2):
        t = threading.Thread(target=func_fs, args=(i,))
        l_thread.append(t)
    for t in l_thread:
        t.start()
    for t in l_thread:
        t.join()
    print(time.time() - start)
```

#### Todo

- lock
- 生产者消费者模型
- Queue 队列
- 爬虫实战

#### 参考链接:

[threading](https://docs.python.org/3.7/library/threading.html?highlight=threading#module-threading)

[_thread](https://docs.python.org/3.7/library/_thread.html?highlight=_thread#module-_thread)
