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