const express = require('express');
const axios = require('axios');
const cors = require('cors');
const path = require('path');

const app = express();
const PORT = process.env.PORT || 3000;

app.use(cors());
app.use(express.json());
app.use(express.urlencoded({ extended: true }));
app.use(express.static(path.join(__dirname, 'public')));

app.get('/', (req, res) => {
  res.sendFile(path.join(__dirname, 'public', 'index.html'));
});

app.post('/api/download', async (req, res) => {
  try {
    const { url } = req.body;
    
    if (!url) {
      return res.status(400).json({ error: '请输入抖音视频链接' });
    }

    const videoId = extractVideoId(url);
    
    if (!videoId) {
      return res.status(400).json({ error: '无效的抖音视频链接' });
    }

    const apiUrl = `https://www.iesdouyin.com/web/api/v2/aweme/iteminfo/?item_ids=${videoId}`;
    
    const response = await axios.get(apiUrl, {
      headers: {
        'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 Mobile/15E148 Safari/604.1',
        'Referer': 'https://www.douyin.com/',
        'Accept': 'application/json'
      }
    });

    const data = response.data;
    
    if (data.item_list && data.item_list.length > 0) {
      const video = data.item_list[0];
      const videoUrl = video.video.play_addr.url_list[0].replace('playwm', 'play');
      
      res.json({
        success: true,
        videoUrl: videoUrl,
        title: video.desc || '抖音视频',
        cover: video.video.cover.url_list[0],
        author: video.author.nickname
      });
    } else {
      res.status(404).json({ error: '未找到视频信息' });
    }
  } catch (error) {
    console.error('解析视频失败:', error);
    res.status(500).json({ error: '解析视频失败，请稍后重试' });
  }
});

function extractVideoId(url) {
  const regex = /(?:v\.douyin\.com\/|douyin\.com\/video\/|iesdouyin\.com\/share\/)([a-zA-Z0-9_-]+)/;
  const match = url.match(regex);
  return match ? match[1] : null;
}

app.listen(PORT, () => {
  console.log(`服务器运行在 http://localhost:${PORT}`);
});