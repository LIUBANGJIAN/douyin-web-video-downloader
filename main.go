package main

import (
	"encoding/json"
	"fmt"
	"net/http"
	"os/exec"
	"path/filepath"
	"regexp"
	"strings"
	"time"
)

type VideoInfo struct {
	Success  bool   `json:"success"`
	VideoURL string `json:"videoUrl"`
	Title    string `json:"title"`
	Author   string `json:"author"`
	Error    string `json:"error"`
}

type YTDLPOutput struct {
	ID       string `json:"id"`
	Title    string `json:"title"`
	Uploader string `json:"uploader"`
	Ext      string `json:"ext"`
	Url      string `json:"url"`
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
		sendResponse(w, VideoInfo{Success: false, Error: "Invalid request"})
		return
	}

	cleanURL := extractDouyinURL(req.URL)
	if cleanURL == "" {
		sendResponse(w, VideoInfo{Success: false, Error: "无效的抖音视频链接"})
		return
	}

	videoID := fmt.Sprintf("%d", time.Now().UnixNano())
	outputPath := filepath.Join("downloads", videoID)
	outputTemplate := outputPath + ".%(ext)s"

	cmd := exec.Command("yt-dlp", "-j", "--no-warnings", "-o", outputTemplate, cleanURL)
	output, err := cmd.CombinedOutput()
	if err != nil {
		sendResponse(w, VideoInfo{Success: false, Error: "下载失败: " + string(output)})
		return
	}

	var ytOutput YTDLPOutput
	if err := json.Unmarshal(output, &ytOutput); err != nil {
		sendResponse(w, VideoInfo{Success: false, Error: "解析响应失败"})
		return
	}

	videoFile := fmt.Sprintf("%s.%s", videoID, ytOutput.Ext)

	sendResponse(w, VideoInfo{
		Success:  true,
		VideoURL: "/download/" + videoFile,
		Title:    ytOutput.Title,
		Author:   ytOutput.Uploader,
	})
}

func extractDouyinURL(text string) string {
	patterns := []string{
		`https?://v\.douyin\.com/[a-zA-Z0-9_-]+/?`,
		`https?://www\.douyin\.com/video/[a-zA-Z0-9_-]+/?`,
		`https?://douyin\.com/video/[a-zA-Z0-9_-]+/?`,
	}

	for _, pattern := range patterns {
		re := regexp.MustCompile(pattern)
		match := re.FindString(text)
		if match != "" {
			return match
		}
	}
	return ""
}

func serveVideo(w http.ResponseWriter, r *http.Request) {
	filename := strings.TrimPrefix(r.URL.Path, "/download/")
	filePath := filepath.Join("downloads", filename)

	w.Header().Set("Content-Type", "video/mp4")
	w.Header().Set("Content-Disposition", "attachment; filename=\""+filename+"\"")
	http.ServeFile(w, r, filePath)
}

func sendResponse(w http.ResponseWriter, info VideoInfo) {
	w.Header().Set("Content-Type", "application/json")
	w.Header().Set("Access-Control-Allow-Origin", "*")
	json.NewEncoder(w).Encode(info)
}
