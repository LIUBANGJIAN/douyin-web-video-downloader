package main

import (
	"encoding/json"
	"fmt"
	"io"
	"net/http"
	"net/url"
	"os"
	"regexp"
	"strings"
)

type VideoInfo struct {
	Success bool   `json:"success"`
	VideoURL string `json:"videoUrl"`
	Title    string `json:"title"`
	Author   string `json:"author"`
	Error    string `json:"error"`
}

func main() {
	http.HandleFunc("/", serveIndex)
	http.HandleFunc("/api/download", downloadHandler)
	http.HandleFunc("/download/", serveVideo)

	fmt.Println("Server running on http://localhost:8080")
	http.ListenAndServe(":8080", nil)
}

func serveIndex(w http.ResponseWriter, r *http.Request) {
	http.ServeFile(w, r, "index.html")
}

func downloadHandler(w http.ResponseWriter, r *http.Request) {
	if r.Method != http.MethodPost {
		http.Error(w, "Method not allowed", http.StatusMethodNotAllowed)
		return
	}

	var req struct {
		URL string `json:"url"`
	}

	if err := json.NewDecoder(r.Body).Decode(&req); err != nil {
		http.Error(w, "Invalid request body", http.StatusBadRequest)
		return
	}

	videoURL := extractDouyinURL(req.URL)
	if videoURL == "" {
		sendResponse(w, VideoInfo{Success: false, Error: "无效的抖音视频链接"})
		return
	}

	videoID := extractVideoID(videoURL)
	if videoID == "" {
		sendResponse(w, VideoInfo{Success: false, Error: "无法提取视频ID"})
		return
	}

	info, err := fetchVideoInfo(videoID)
	if err != nil {
		sendResponse(w, VideoInfo{Success: false, Error: err.Error()})
		return
	}

	videoFile, err := downloadVideo(info.VideoURL)
	if err != nil {
		sendResponse(w, VideoInfo{Success: false, Error: "视频下载失败: " + err.Error()})
		return
	}

	sendResponse(w, VideoInfo{
		Success: true,
		VideoURL: "/download/" + videoFile,
		Title:    info.Title,
		Author:   info.Author,
	})
}

func extractDouyinURL(input string) string {
	patterns := []string{
		`https?://v\.douyin\.com/[a-zA-Z0-9_-]+/?`,
		`https?://www\.douyin\.com/video/[a-zA-Z0-9_-]+/?`,
		`https?://douyin\.com/video/[a-zA-Z0-9_-]+/?`,
	}

	for _, pattern := range patterns {
		re := regexp.MustCompile(pattern)
		match := re.FindString(input)
		if match != "" {
			return match
		}
	}
	return ""
}

func extractVideoID(douyinURL string) string {
	u, err := url.Parse(douyinURL)
	if err != nil {
		return ""
	}

	if strings.Contains(u.Host, "v.douyin.com") {
		return strings.TrimPrefix(u.Path, "/")
	}

	re := regexp.MustCompile(`/video/([a-zA-Z0-9_-]+)`)
	match := re.FindStringSubmatch(u.Path)
	if len(match) > 1 {
		return match[1]
	}

	return ""
}

type DouyinResponse struct {
	ItemList []struct {
		Desc   string `json:"desc"`
		Author struct {
			Nickname string `json:"nickname"`
		} `json:"author"`
		Video struct {
			PlayAddr struct {
				URLList []string `json:"url_list"`
			} `json:"play_addr"`
		} `json:"video"`
	} `json:"item_list"`
}

func fetchVideoInfo(videoID string) (*VideoInfo, error) {
	apiURL := fmt.Sprintf("https://www.iesdouyin.com/web/api/v2/aweme/iteminfo/?item_ids=%s", videoID)

	client := &http.Client{}
	req, err := http.NewRequest("GET", apiURL, nil)
	if err != nil {
		return nil, err
	}

	req.Header.Set("User-Agent", "Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 Mobile/15E148 Safari/604.1")
	req.Header.Set("Referer", "https://www.douyin.com/")

	resp, err := client.Do(req)
	if err != nil {
		return nil, err
	}
	defer resp.Body.Close()

	body, err := io.ReadAll(resp.Body)
	if err != nil {
		return nil, err
	}

	var data DouyinResponse
	if err := json.Unmarshal(body, &data); err != nil {
		return nil, err
	}

	if len(data.ItemList) == 0 {
		return nil, fmt.Errorf("未找到视频信息")
	}

	video := data.ItemList[0]
	playURL := video.Video.PlayAddr.URLList[0]
	playURL = strings.Replace(playURL, "playwm", "play", 1)

	return &VideoInfo{
		VideoURL: playURL,
		Title:    video.Desc,
		Author:   video.Author.Nickname,
	}, nil
}

func downloadVideo(videoURL string) (string, error) {
	resp, err := http.Get(videoURL)
	if err != nil {
		return "", err
	}
	defer resp.Body.Close()

	filename := fmt.Sprintf("%d.mp4", os.Getpid())
	filePath := "downloads/" + filename

	if err := os.MkdirAll("downloads", 0755); err != nil {
		return "", err
	}

	file, err := os.Create(filePath)
	if err != nil {
		return "", err
	}
	defer file.Close()

	_, err = io.Copy(file, resp.Body)
	if err != nil {
		return "", err
	}

	return filename, nil
}

func serveVideo(w http.ResponseWriter, r *http.Request) {
	filename := strings.TrimPrefix(r.URL.Path, "/download/")
	filePath := "downloads/" + filename

	w.Header().Set("Content-Type", "video/mp4")
	w.Header().Set("Content-Disposition", "attachment; filename=\""+filename+"\"")
	http.ServeFile(w, r, filePath)
}

func sendResponse(w http.ResponseWriter, info VideoInfo) {
	w.Header().Set("Content-Type", "application/json")
	w.Header().Set("Access-Control-Allow-Origin", "*")
	json.NewEncoder(w).Encode(info)
}
