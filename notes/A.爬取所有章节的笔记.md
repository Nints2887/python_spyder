一，分析网页
===

![](E:/03py_spider/project/01get_text/01%E7%93%A6%E5%B0%94%E7%99%BB%E6%B9%96/1.1.2summary/image-20250601141343380.png)

![](E:/03py_spider/project/01get_text/01%E7%93%A6%E5%B0%94%E7%99%BB%E6%B9%96/1.1.2summary/image-20250601141540637.png)

通过分析上述两张图片我们就知道了面对这种没有反爬机制的小说网站该如何处理：**找到资源的位置和结构，直接拿取**！！！

---



二，代码预览
===

```py
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import os
import time
import re

def get_chapter_links(directory_url, base_domain):
    """提取章节链接（精确匹配HTML结构：div.xslttext > ul > li > a）"""
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36'
    }
    response = requests.get(directory_url, headers=headers)
    response.encoding = response.apparent_encoding
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # 逐层查找元素：div.xslttext → ul → li → a
    chapter_div = soup.find('div', class_='xslttext')  # 外层div
    if not chapter_div:
        print("错误：未找到class为'xslttext'的div元素")
        return []
    
    chapter_ul = chapter_div.find('ul')  # ul列表
    if not chapter_ul:
        print("错误：div.xslttext下未找到ul元素")
        return []
    
    chapter_links = []
    for li in chapter_ul.find_all('li'):  # 每个章节的li
        a_tag = li.find('a')  # 章节链接的a标签
        if a_tag and 'href' in a_tag.attrs:
            chapter_url = urljoin(base_domain, a_tag['href'])
            chapter_title = a_tag.get_text(strip=True)
            chapter_links.append((chapter_title, chapter_url))
    
    return chapter_links

def sanitize_filename(filename):
    """清理文件名中的非法字符"""
    return re.sub(r'[\\/*?:"<>|]', "_", filename)

def extract_chapter_content(chapter_url):
    """提取单个章节内容（div#dashu_text下的p标签）"""
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36'
    }
    try:
        response = requests.get(chapter_url, headers=headers, timeout=10)
        response.raise_for_status()
        response.encoding = response.apparent_encoding
        soup = BeautifulSoup(response.text, 'html.parser')
        
        content_div = soup.find('div', id='dashu_text')  # 内容区域
        if not content_div:
            print(f"警告：章节 {chapter_url} 未找到内容区域（id='dashu_text'）")
            return ""
        
        # 提取所有段落文本并合并
        paragraphs = [p.get_text(strip=True) for p in content_div.find_all('p')]
        return '\n'.join(paragraphs)
    
    except Exception as e:
        print(f"获取章节 {chapter_url} 失败：{e}")
        return ""

def crawl_all_chapters(directory_url, base_domain, output_dir="novel_chapters"):
    """爬取所有章节并按章节保存到独立文件夹"""
    # 创建主目录
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    chapter_links = get_chapter_links(directory_url, base_domain)
    total_chapters = len(chapter_links)
    
    if not chapter_links:
        print("没有找到任何章节链接，爬取终止")
        return
    
    for idx, (title, link) in enumerate(chapter_links, 1):
        safe_title = sanitize_filename(title)
        chapter_dir = os.path.join(output_dir, f"{idx:03d}_{safe_title}")  # 章节文件夹（编号_标题）
        os.makedirs(chapter_dir, exist_ok=True)  # 确保目录存在
        
        print(f"开始爬取第 {idx} 章：{title}（链接：{link}）")
        content = extract_chapter_content(link)
        
        if content:
            # 保存章节内容
            content_path = os.path.join(chapter_dir, "content.txt")
            with open(content_path, "w", encoding="utf-8") as f:
                f.write(content)
            print(f"  内容保存到：{content_path}")
        
        time.sleep(1)  # 反爬延时，避免过快请求
    
    print(f"爬取完成！共 {total_chapters} 个章节，保存到 {output_dir} 目录")

if __name__ == "__main__":
    base_domain = "http://www.newxue.com"  # 网站基础域名
    directory_url = "http://www.newxue.com/waerdenghu/"  # 小说目录页URL
    crawl_all_chapters(directory_url, base_domain)
```

---

二，代码各个部分讲解
===



1. ## """提取章节链接（精确匹配HTML结构：div.xslttext > ul > li > a）"""
---

```py
def get_chapter_links(directory_url, base_domain):
    """提取章节链接（精确匹配HTML结构：div.xslttext > ul > li > a）"""
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36'
    }
    response = requests.get(directory_url, headers=headers)
    response.encoding = response.apparent_encoding
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # 逐层查找元素：div.xslttext → ul → li → a
    chapter_div = soup.find('div', class_='xslttext')  # 外层div
    if not chapter_div:
        print("错误：未找到class为'xslttext'的div元素")
        return []
    
    chapter_ul = chapter_div.find('ul')  # ul列表
    if not chapter_ul:
        print("错误：div.xslttext下未找到ul元素")
        return []
    
    chapter_links = []
    for li in chapter_ul.find_all('li'):  # 每个章节的li
        a_tag = li.find('a')  # 章节链接的a标签
        if a_tag and 'href' in a_tag.attrs:
            chapter_url = urljoin(base_domain, a_tag['href'])
            """
            这是一段代码片段，`urljoin` 通常是用于拼接URL的函数。`base_domain` 代表基础域名，比如 "https://example.com" 这种形式。`a_tag['href']` 表示从HTML的 `<a>` 标签（超链接标签）中获取的 `href` 属性值，该属性值可能是相对路径，如 "/page1" 或者是完整的URL 。`urljoin` 函数的作用就是将 `base_domain` 和 `a_tag['href']` 正确地拼接在一起，生成一个完整可用的URL 。例如 `base_domain` 为 "https://example.com" ，`a_tag['href']` 为 "/about" ，拼接后可能得到 "https://example.com/about" 。 
            """
            chapter_title = a_tag.get_text(strip=True)
            """
            这行代码的含义是获取 `a_tag` 所代表的HTML标签内的文本内容，并通过 `strip=True` 参数去除文本前后的空白字符（包括空格、制表符、换行符等）。例如，如果 `a_tag` 是 `<a href="#"> 示例文本 </a>`，执行此代码后会得到 “示例文本”，前后空白字符被去除。 这里 `a_tag` 通常是通过类似BeautifulSoup等解析HTML的库获取到的一个代表 `<a>` 标签的对象，`get_text()` 是该对象的方法，用于提取文本，`strip` 参数是对提取文本的处理方式设定。 
            """
          
            chapter_links.append((chapter_title, chapter_url))
    
    return chapter_links
```

这是一个Python函数`get_chapter_links`，功能是从给定的网页目录链接中提取章节链接。具体解释如下：

- **函数定义及功能描述**：`def get_chapter_links(directory_url, base_domain)`，此函数接受两个参数，`directory_url`为网页目录链接，`base_domain`是基础域名。函数的功能描述为“提取章节链接（精确匹配HTML结构：div.xslttext > ul > li > a）”，即从特定HTML结构的网页中获取章节链接。
- **设置请求头**：定义了`headers`，模拟浏览器请求头，`User - Agent`设置为常见的Chrome浏览器标识，用于向服务器发送请求，避免被识别为非浏览器访问而拒绝请求。
- **发送请求并处理响应**：使用`requests.get`方法发送HTTP GET请求到`directory_url`，并设置`headers`。`response.encoding = response.apparent_encoding`用于自动检测并设置响应内容的编码，避免乱码问题。然后使用`BeautifulSoup`库将响应的文本解析为HTML对象`soup`。
- **查找特定HTML结构元素**：通过逐层查找特定的HTML元素来获取章节链接。首先查找`class`为`xslttext`的`div`元素，若未找到则打印错误信息并返回空列表。接着在找到的`div`元素下查找`ul`元素，若未找到同样打印错误信息并返回空列表。
- **提取章节链接**：遍历`ul`元素下的所有`li`元素，在每个`li`元素中查找`a`标签。若`a`标签存在且包含`href`属性，则使用`urljoin`函数将相对链接与`base_domain`拼接成完整的章节链接`chapter_url`，并获取`a`标签的文本内容作为章节标题`chapter_title`，将标题和链接以元组形式添加到`chapter_links`列表中。
- **返回结果**：最终返回包含所有章节标题和链接元组的`chapter_links`列表。

例如，若`directory_url`是一个小说目录页链接，`base_domain`是该小说网站的域名，此函数就能从该目录页提取出每个章节的标题和对应的链接。 



2.  """清理文件名中的非法字符"""
---

```py
def sanitize_filename(filename):
    """清理文件名中的非法字符"""
    return re.sub(r'[\\/*?:"<>|]', "_", filename)
```

这是一段Python代码中的函数定义。

`def sanitize_filename(filename):` 定义了一个名为 `sanitize_filename` 的函数，该函数接受一个参数 `filename`，即文件名。

`return re.sub(r'[\\/*?:"<>|]', "_", filename)` 这行代码使用 `re` 模块（Python的正则表达式模块）的 `sub` 函数，将 `filename` 中匹配正则表达式 `[\\/*?:"<>|]` 的字符替换为下划线 `_`，并返回处理后的文件名。这里的正则表达式 `[\\/*?:"<>|]` 列出了一些在文件名中通常不允许出现的非法字符，如反斜杠、正斜杠、星号、问号、冒号、双引号、小于号、大于号、竖线等。通过这个函数，输入的文件名中的这些非法字符会被替换为下划线，从而得到一个合法可用的文件名。例如，若输入文件名 `new/file:name.txt`，经过该函数处理后，会返回 `new_file_name.txt` 。 





3."""提取单个章节内容（div#dashu_text下的p标签）"""
---

```py
def extract_chapter_content(chapter_url):
    """提取单个章节内容（div#dashu_text下的p标签）"""
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36'
    }
    try:
        response = requests.get(chapter_url, headers=headers, timeout=10)
        response.raise_for_status()
        response.encoding = response.apparent_encoding
        soup = BeautifulSoup(response.text, 'html.parser')
        
        content_div = soup.find('div', id='dashu_text')  # 内容区域
        """
        这行代码是在Python的BeautifulSoup库中使用的操作。`soup`通常是一个已被解析的HTML或XML文档对象。`find`方法用于在文档中查找符合特定条件的第一个元素。这里是查找一个`div`标签，并且这个`div`标签的`id`属性值为`dashu_text`，这一操作的目的是定位到具有该特定`id`的`div`元素，这个元素被注释标记为“内容区域”，可能后续代码会对这个找到的元素进行内容提取、修改等操作。 例如，如果有一个HTML文档，其中包含`<div id="dashu_text">这里是要找的内容</div>`，通过这行代码就能找到这个包含特定内容的`div`元素。 
     	"""
        if not content_div:
            print(f"警告：章节 {chapter_url} 未找到内容区域（id='dashu_text'）")
            return ""
        
        # 提取所有段落文本并合并
        paragraphs = [p.get_text(strip=True) for p in content_div.find_all('p')]
        """
        这行代码的作用是从`content_div`中查找所有的`<p>`标签，并提取每个`<p>`标签内的文本内容，同时去除文本两端的空白字符，最后将这些提取的文本内容以列表形式存储在`paragraphs`变量中。具体解释如下：
1. `content_div.find_all('p')`：这部分代码使用`find_all`方法在`content_div`对象（通常是一个网页解析后的节点对象，比如`BeautifulSoup`解析网页后的某个节点）中查找所有的`<p>`标签元素，返回一个包含所有找到的`<p>`标签的列表。
2. `p.get_text(strip=True)`：对于`find_all('p')`返回列表中的每个`<p>`标签对象`p`，使用`get_text`方法获取其内部包含的文本内容。`strip=True`参数表示在获取文本时，去除文本两端的空白字符（如空格、换行符等）。
3. `[p.get_text(strip=True) for p in content_div.find_all('p')]`：这是一个列表推导式，它遍历`content_div.find_all('p')`返回的列表，对每个`<p>`标签对象`p`执行`p.get_text(strip=True)`操作，并将结果组成一个新的列表。
4. `paragraphs = [p.get_text(strip=True) for p in content_div.find_all('p')]`：将通过列表推导式生成的包含提取文本的列表赋值给变量`paragraphs`。

例如，假设`content_div`对应的HTML片段为`<div class="content"><p>  第一段文本  </p><p>第二段文本</p></div>`，执行上述代码后，`paragraphs`列表内容为`['第一段文本', '第二段文本']` 。 
		"""
        return '\n'.join(paragraphs)
    
    except Exception as e:
        print(f"获取章节 {chapter_url} 失败：{e}")
        return ""
```

这是一段Python代码中的函数定义及相关注释。`def extract_chapter_content(chapter_url):`定义了一个名为`extract_chapter_content`的函数，它接受一个参数`chapter_url`，用于提取单个章节的内容。

“提取单个章节内容（div#dashu_text下的p标签）”是对该函数功能的注释说明，表明此函数旨在从网页中特定元素（`div`标签且`id`为`dashu_text`内的`p`标签）提取内容。

函数内部，首先设置了请求头`headers`，模拟浏览器发送请求。然后使用`requests.get`尝试获取`chapter_url`对应的网页内容，设置了超时时间为10秒。若请求成功，调整编码为网页实际编码，并使用`BeautifulSoup`解析网页。接着查找`id`为`dashu_text`的`div`标签作为内容区域，若未找到则打印警告并返回空字符串。最后提取该区域内所有`p`标签的文本并合并，以换行符分隔后返回。若在获取或处理过程中出现异常，打印错误信息并返回空字符串。 





4."""爬取所有章节并按章节保存到独立文件夹"""
---

```py
def crawl_all_chapters(directory_url, base_domain, output_dir="novel_chapters"):
    """爬取所有章节并按章节保存到独立文件夹"""
    # 创建主目录
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    chapter_links = get_chapter_links(directory_url, base_domain)
    total_chapters = len(chapter_links)
    
    if not chapter_links:
        print("没有找到任何章节链接，爬取终止")
        return
    
    for idx, (title, link) in enumerate(chapter_links, 1):
        safe_title = sanitize_filename(title)
        chapter_dir = os.path.join(output_dir, f"{idx:03d}_{safe_title}")  # 章节文件夹（编号_标题）
        os.makedirs(chapter_dir, exist_ok=True)  # 确保目录存在
        
        print(f"开始爬取第 {idx} 章：{title}（链接：{link}）")
        content = extract_chapter_content(link)
        
        if content:
            # 保存章节内容
            content_path = os.path.join(chapter_dir, "content.txt")
            with open(content_path, "w", encoding="utf-8") as f:
                f.write(content)
            print(f"  内容保存到：{content_path}")
        
        time.sleep(1)  # 反爬延时，避免过快请求
    
    print(f"爬取完成！共 {total_chapters} 个章节，保存到 {output_dir} 目录")
```

这是一段Python代码，定义了一个名为`crawl_all_chapters`的函数，其功能是爬取小说所有章节并按章节保存到独立文件夹。具体解释如下：
1. **函数定义及参数**：
    - `def crawl_all_chapters(directory_url, base_domain, output_dir="novel_chapters"):` 定义了一个函数，`directory_url`为小说目录页面的URL，`base_domain`是基础域名，`output_dir`指定保存章节的主目录，默认值为`novel_chapters`。
2. **函数文档字符串**：
    - `爬取所有章节并按章节保存到独立文件夹` 对函数功能进行简要描述。
3. **创建主目录**：
    - `if not os.path.exists(output_dir):` 检查指定的输出目录是否存在，如果不存在则使用`os.makedirs(output_dir)`创建该目录。
4. **获取章节链接**：
    - `chapter_links = get_chapter_links(directory_url, base_domain)` 调用`get_chapter_links`函数获取所有章节的链接，`total_chapters = len(chapter_links)`计算章节总数。
    - `if not chapter_links:` 如果没有获取到章节链接，打印提示信息“没有找到任何章节链接，爬取终止”并返回，结束函数执行。
5. **遍历章节链接并爬取内容**：
    - `for idx, (title, link) in enumerate(chapter_links, 1):` 遍历所有章节链接，`idx`为章节编号，`title`为章节标题，`link`为章节链接。
    - `safe_title = sanitize_filename(title)` 对章节标题进行处理，使其符合文件名规范。
    - `chapter_dir = os.path.join(output_dir, f"{idx:03d}_{safe_title}")` 创建每个章节的文件夹，格式为“三位数字编号_标题”。
    - `os.makedirs(chapter_dir, exist_ok=True)` 确保章节文件夹存在。
    - `print(f"开始爬取第 {idx} 章：{title}（链接：{link}）")` 打印正在爬取的章节信息。
    - `content = extract_chapter_content(link)` 调用`extract_chapter_content`函数提取章节内容。
    - `if content:` 如果成功提取到内容，将内容保存到章节文件夹下的`content.txt`文件中，并打印保存路径。
    - `time.sleep(1)` 每次爬取后暂停1秒，防止请求过快被网站识别为爬虫而限制访问。
6. **爬取完成提示**：
    - `print(f"爬取完成！共 {total_chapters} 个章节，保存到 {output_dir} 目录")` 打印爬取完成的信息，包括章节总数和保存目录。

例如，假设`directory_url`是一部小说目录页的地址，`base_domain`是该小说网站的基础域名，`output_dir`为`my_novel`，函数执行后会在`my_novel`目录下创建多个以章节编号和标题命名的文件夹，每个文件夹内保存对应章节的内容。 
