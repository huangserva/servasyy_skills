#!/usr/bin/env python3
"""
单条 Twitter 推文爬取脚本
支持通过推文 URL 或 ID 获取单条推文的详细信息
"""
import argparse
import json
import re
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any

# 添加 trend-crawler 的虚拟环境
TREND_CRAWLER_PATH = Path.home() / "Documents" / "trend-crawler-master" / "trend-crawler"

from tweety import Twitter
import yaml


class SingleTweetFetcher:
    """单条推文爬取器"""
    
    def __init__(self, auth_token: Optional[str] = None):
        """
        初始化爬取器
        
        Args:
            auth_token: Twitter auth_token，如果不提供则从配置文件读取
        """
        self.auth_token = auth_token
        
        # 尝试从 trend-crawler 的配置加载
        if not self.auth_token:
            trend_config = TREND_CRAWLER_PATH / "config.yaml"
            if trend_config.exists():
                self.auth_token = self._load_auth_token(str(trend_config))
        
        # 创建 Twitter 实例
        self.app = Twitter("session")
        if self.auth_token:
            self.app.load_auth_token(self.auth_token)
            print("✅ 已加载 auth_token")
        else:
            print("⚠️  未配置 auth_token，使用访客模式（可能受限）")
    
    def _load_auth_token(self, config_path: str) -> Optional[str]:
        """从配置文件加载 auth_token"""
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)
                return config.get('twitter_accounts', {}).get('auth_token')
        except Exception as e:
            print(f"⚠️  加载配置失败: {e}")
            return None
    
    @staticmethod
    def parse_tweet_url(url_or_id: str) -> tuple:
        """
        解析推文 URL 或 ID
        
        Args:
            url_or_id: 推文 URL 或 ID
            
        Returns:
            (tweet_id, username) 元组，username 可能为 None
        """
        # 匹配 URL 格式: https://x.com/username/status/1234567890
        # 或 https://twitter.com/username/status/1234567890
        url_pattern = r'(?:https?://)?(?:www\.)?(?:twitter\.com|x\.com)/(\w+)/status/(\d+)'
        match = re.match(url_pattern, url_or_id)
        
        if match:
            username = match.group(1)
            tweet_id = match.group(2)
            return tweet_id, username
        
        # 纯数字 ID
        if url_or_id.isdigit():
            return url_or_id, None
        
        raise ValueError(f"无法解析推文 URL 或 ID: {url_or_id}")
    
    def get_tweet(self, tweet_id: str, username: Optional[str] = None) -> Dict[str, Any]:
        """
        获取单条推文
        
        Args:
            tweet_id: 推文 ID
            username: 用户名（可选，用于构建 URL）
            
        Returns:
            推文详情字典
        """
        try:
            # 使用 tweety 获取推文
            tweet = self.app.tweet_detail(tweet_id)
            
            if not tweet:
                return {'success': False, 'error': '推文不存在或已被删除'}
            
            # 获取作者信息
            author = tweet.author if hasattr(tweet, 'author') else None
            author_username = author.username if author else username
            author_name = author.name if author else None
            author_id = author.id if author else None
            author_followers = author.followers_count if author and hasattr(author, 'followers_count') else None
            author_verified = author.verified if author and hasattr(author, 'verified') else False
            author_bio = author.description if author and hasattr(author, 'description') else None
            author_profile_image = author.profile_image_url_https if author and hasattr(author, 'profile_image_url_https') else None
            
            # 获取媒体
            media_list = []
            if hasattr(tweet, 'media') and tweet.media:
                for m in tweet.media:
                    media_item = {
                        'type': getattr(m, 'type', 'unknown'),
                        'url': getattr(m, 'media_url_https', None) or getattr(m, 'url', None),
                    }
                    if hasattr(m, 'video_info'):
                        media_item['video_url'] = getattr(m.video_info, 'url', None)
                    media_list.append(media_item)
            
            # 获取引用/回复的推文
            quoted_tweet = None
            if hasattr(tweet, 'quoted_tweet') and tweet.quoted_tweet:
                qt = tweet.quoted_tweet
                quoted_tweet = {
                    'id': qt.id,
                    'text': qt.text,
                    'author': qt.author.username if qt.author else None,
                }
            
            reply_to = None
            if hasattr(tweet, 'reply_to') and tweet.reply_to:
                reply_to = tweet.reply_to
            
            # 获取互动数据
            likes = getattr(tweet, 'likes', 0) or 0
            retweets = getattr(tweet, 'retweet_counts', 0) or 0
            replies = getattr(tweet, 'reply_counts', 0) or 0
            quotes = getattr(tweet, 'quote_counts', 0) or 0
            views = getattr(tweet, 'views', 0)
            if views == 'Unavailable':
                views = 0
            views = int(views) if views else 0
            
            # 获取实体信息
            hashtags = []
            mentions = []
            urls = []
            
            if hasattr(tweet, 'hashtags') and tweet.hashtags:
                hashtags = [h.text if hasattr(h, 'text') else str(h) for h in tweet.hashtags]
            
            if hasattr(tweet, 'user_mentions') and tweet.user_mentions:
                mentions = [m.username if hasattr(m, 'username') else str(m) for m in tweet.user_mentions]
            
            if hasattr(tweet, 'urls') and tweet.urls:
                urls = [u.expanded_url if hasattr(u, 'expanded_url') else str(u) for u in tweet.urls]
            
            # 构建结果
            result = {
                'success': True,
                'tweet': {
                    'id': tweet.id,
                    'text': tweet.text,
                    'created_at': str(tweet.created_on) if hasattr(tweet, 'created_on') else None,
                    'language': getattr(tweet, 'language', None),
                    'source': getattr(tweet, 'source', None),
                    'url': f"https://x.com/{author_username}/status/{tweet.id}" if author_username else None,
                    
                    # 互动数据
                    'metrics': {
                        'like_count': likes,
                        'retweet_count': retweets,
                        'reply_count': replies,
                        'quote_count': quotes,
                        'view_count': views,
                    },
                    
                    # 推文类型
                    'is_retweet': getattr(tweet, 'is_retweet', False) or False,
                    'is_quote': getattr(tweet, 'is_quoted', False) or False,
                    'is_reply': getattr(tweet, 'is_reply', False) or False,
                    
                    # 媒体
                    'media': media_list,
                    'has_media': len(media_list) > 0,
                    
                    # 实体
                    'entities': {
                        'hashtags': hashtags,
                        'mentions': mentions,
                        'urls': urls,
                    },
                    
                    # 引用/回复
                    'quoted_tweet': quoted_tweet,
                    'reply_to': reply_to,
                },
                'author': {
                    'id': author_id,
                    'username': author_username,
                    'name': author_name,
                    'followers_count': author_followers,
                    'verified': author_verified,
                    'bio': author_bio,
                    'profile_image_url': author_profile_image,
                },
                'fetched_at': datetime.now().isoformat(),
            }
            
            return result
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def to_markdown(self, data: Dict[str, Any]) -> str:
        """
        将推文数据转换为 Markdown 格式
        
        Args:
            data: 推文数据字典
            
        Returns:
            Markdown 字符串
        """
        if not data.get('success'):
            return f"# 获取推文失败\n\n错误: {data.get('error', '未知错误')}"
        
        tweet = data['tweet']
        author = data['author']
        
        lines = []
        
        # 标题
        lines.append(f"# @{author['username']} 的推文")
        lines.append("")
        lines.append(f"> 爬取时间: {data['fetched_at']}")
        lines.append("")
        
        # 作者信息
        lines.append("## 作者信息")
        lines.append("")
        lines.append(f"- **名称**: {author['name']}")
        lines.append(f"- **用户名**: @{author['username']}")
        if author.get('followers_count'):
            lines.append(f"- **粉丝**: {author['followers_count']:,}")
        if author.get('verified'):
            lines.append("- **认证**: ✅")
        if author.get('bio'):
            lines.append(f"- **简介**: {author['bio'][:200]}")
        lines.append("")
        
        # 推文内容
        lines.append("## 推文内容")
        lines.append("")
        lines.append(f"**发布时间**: {tweet['created_at']}")
        lines.append("")
        
        # 推文文本
        text = tweet['text'].replace('\n', '\n> ')
        lines.append(f"> {text}")
        lines.append("")
        
        # 互动数据
        metrics = tweet['metrics']
        stats = [
            f"❤️ {metrics['like_count']:,}",
            f"🔁 {metrics['retweet_count']:,}",
            f"💬 {metrics['reply_count']:,}",
        ]
        if metrics.get('quote_count'):
            stats.append(f"🔗 {metrics['quote_count']:,}")
        if metrics.get('view_count'):
            stats.append(f"👁 {metrics['view_count']:,}")
        
        lines.append(f"**互动**: {' | '.join(stats)}")
        lines.append("")
        
        # 链接
        if tweet.get('url'):
            lines.append(f"**链接**: [{tweet['url']}]({tweet['url']})")
            lines.append("")
        
        # 媒体
        if tweet.get('media'):
            lines.append("## 媒体")
            lines.append("")
            for i, m in enumerate(tweet['media'], 1):
                if m.get('url'):
                    lines.append(f"![媒体 {i}]({m['url']})")
            lines.append("")
        
        # 实体
        entities = tweet.get('entities', {})
        if entities.get('hashtags'):
            lines.append(f"**话题标签**: {' '.join(['#' + h for h in entities['hashtags']])}")
            lines.append("")
        
        if entities.get('mentions'):
            lines.append(f"**提及用户**: {' '.join(['@' + m for m in entities['mentions']])}")
            lines.append("")
        
        # 引用推文
        if tweet.get('quoted_tweet'):
            qt = tweet['quoted_tweet']
            lines.append("## 引用的推文")
            lines.append("")
            lines.append(f"**来自**: @{qt.get('author', 'unknown')}")
            lines.append(f"> {qt.get('text', '')[:280]}")
            lines.append("")
        
        return '\n'.join(lines)
    
    def to_xscore_format(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        转换为 XScore 项目兼容的格式
        
        Args:
            data: 推文数据字典
            
        Returns:
            XScore 兼容的推文格式
        """
        if not data.get('success'):
            return None
        
        tweet = data['tweet']
        author = data['author']
        metrics = tweet['metrics']
        entities = tweet.get('entities', {})
        
        return {
            'id': tweet['id'],
            'text': tweet['text'],
            'created_at': tweet['created_at'],
            'author': {
                'id': author['id'],
                'username': author['username'],
                'name': author['name'],
                'verified': author.get('verified', False),
                'followers_count': author.get('followers_count'),
                'bio': author.get('bio'),
                'profile_image_url': author.get('profile_image_url'),
            },
            'metrics': {
                'like_count': metrics['like_count'],
                'retweet_count': metrics['retweet_count'],
                'reply_count': metrics['reply_count'],
                'quote_count': metrics.get('quote_count', 0),
                'view_count': metrics.get('view_count', 0),
            },
            'media': tweet.get('media', []),
            'entities': {
                'hashtags': entities.get('hashtags', []),
                'mentions': entities.get('mentions', []),
                'urls': entities.get('urls', []),
            },
        }


def main():
    parser = argparse.ArgumentParser(description='获取单条 Twitter 推文')
    parser.add_argument('url_or_id', help='推文 URL 或 ID（如 https://x.com/user/status/123 或 123）')
    parser.add_argument('-o', '--output', help='输出文件路径')
    parser.add_argument('--json', action='store_true', help='输出 JSON 格式')
    parser.add_argument('--xscore', action='store_true', help='输出 XScore 兼容格式')
    parser.add_argument('--auth-token', help='Twitter auth_token')
    parser.add_argument('--quiet', '-q', action='store_true', help='安静模式，只输出结果')
    
    args = parser.parse_args()
    
    # 创建爬取器
    fetcher = SingleTweetFetcher(auth_token=args.auth_token)
    
    # 解析 URL 或 ID
    try:
        tweet_id, username = fetcher.parse_tweet_url(args.url_or_id)
        if not args.quiet:
            print(f"\n📋 获取推文 ID: {tweet_id}")
    except ValueError as e:
        print(f"❌ {e}")
        sys.exit(1)
    
    # 获取推文
    data = fetcher.get_tweet(tweet_id, username)
    
    if not data.get('success'):
        print(f"❌ 获取失败: {data.get('error')}")
        sys.exit(1)
    
    if not args.quiet:
        print(f"✅ 获取成功!")
        print(f"   作者: @{data['author']['username']}")
        print(f"   点赞: {data['tweet']['metrics']['like_count']:,}")
    
    # 输出结果
    if args.xscore:
        output = fetcher.to_xscore_format(data)
        output_str = json.dumps(output, ensure_ascii=False, indent=2)
    elif args.json:
        output_str = json.dumps(data, ensure_ascii=False, indent=2)
    else:
        output_str = fetcher.to_markdown(data)
    
    # 保存或打印
    if args.output:
        output_path = Path(args.output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(output_str)
        if not args.quiet:
            print(f"💾 已保存到: {output_path}")
    else:
        print("\n" + "=" * 60)
        print(output_str)


if __name__ == '__main__':
    main()
