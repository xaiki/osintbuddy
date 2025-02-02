package google

import (
	"encoding/json"
	"fmt"
	"log"
	"net/url"
	"strconv"
	"time"

	"github.com/gocolly/colly"
	"github.com/gocolly/colly/queue"
)

func setHeaders(r *colly.Request) {
	r.Headers.Set("Host", "www.google.com")
	r.Headers.Set("User-Agent", "Mozilla/5.0 (X11; Linux x86_64; rv:102.0) Gecko/20100101 Firefox/102.0")
	r.Headers.Set("Accept", "text/html")
	r.Headers.Set("Accept-Language", "en-US,en;q=0.5")
	r.Headers.Set("Accept-Encoding", "text/html")
	r.Headers.Set("Connection", "keep-alive")
	r.Headers.Set("Upgrade-Insecure-Requests", "1")
	r.Headers.Set("Sec-Fetch-Dest", "document")
	r.Headers.Set("Sec-Fetch-Mode", "navigate")
	r.Headers.Set("Sec-Fetch-Site", "same-site")
	r.Headers.Set("TE", "trailers")
}

type SearchResult struct {
	Title       string `json:"title"`
	Description string `json:"description"`
	Link        string `json:"link"`
	Breadcrumb  string `json:"breadcrumb"`
	Index       int    `json:"index"`
}

type VideoResult struct {
	Title       string `json:"title"`
	Description string `json:"description"`
	Link        string `json:"link"`
	Index       int    `json:"index"`
}

type QuestionResult struct {
	Question string `json:"question"`
}

type StoriesResult struct {
	Link        string `json:"link"`
	Description string `json:"description"`
	Index       int    `json:"index"`
}

type StatsResult struct {
	Related []string `json:"related"`
	Result  []string `json:"result"`
}

type SerpResults struct {
	Stories   []StoriesResult  `json:"stories"`
	Videos    []VideoResult    `json:"videos"`
	Questions []QuestionResult `json:"questions"`
	Search    []SearchResult   `json:"search"`
	Stats     []StatsResult    `json:"stats"`
}

var serpResults = new(SerpResults)

func CrawlGoogle(searchQuery string, pages string) {
	var resultIndex int = 0
	var paginationIndex = 1
	totalPages, err := strconv.Atoi(pages)
	if err != nil {
		panic(err)
	}

	var initialUrl string = fmt.Sprintf("https://www.google.com/search?q=%s&client=firefox-b-e", url.QueryEscape(searchQuery))
	var nextPage string = ""

	// Create a new collector
	c := colly.NewCollector()
	// proxy
	// rp, err := proxy.RoundRobinProxySwitcher()
	// if err != nil {
	// log.Fatal(err)
	// }
	// c.SetProxyFunc(rp)
	c.Limit(&colly.LimitRule{
		DomainGlob:  "*google.*",
		Parallelism: 2,
		RandomDelay: 2 * time.Second,
	})
	if err != nil {
		log.Fatal(err)
	}
	c.SetRequestTimeout(10 * time.Second)

	q, _ := queue.New(
		2, // Number of consumer threads
		&queue.InMemoryQueueStorage{MaxSize: 10000}, // Use default queue storage
	)

	c.OnRequest(func(r *colly.Request) {
		setHeaders(r)
	})

	c.OnResponse(func(r *colly.Response) {
		// r.Save(fmt.Sprintf("%d.html", paginationIndex))
		paginationIndex += 1
	})

	// Set HTML callback for pagination
	c.OnHTML("#pnnext", func(e *colly.HTMLElement) {
		link := e.Attr("href")
		if paginationIndex <= totalPages {
			q.AddURL(fmt.Sprintf("https://google.com/%sclient=firefox-b-e", link))
		}
	})
	resultStats := new(StatsResult)
	// parse related searches
	c.OnHTML("div.s75CSd.OhScic.AB4Wff", func(e *colly.HTMLElement) {
		relatedSearch := e.Text
		resultStats.Related = append(resultStats.Related, relatedSearch)
	})
	// parse about stats at top of page e.g. 'About 83,000,000 results (0.22 seconds) '
	c.OnHTML("#result-stats", func(e *colly.HTMLElement) {
		result := e.Text
		resultStats.Result = append(resultStats.Result, result)
		serpResults.Stats = append(serpResults.Stats, *resultStats)
		resultStats.Related = nil
		resultStats.Result = nil
	})

	// parse top 'top stories' section
	c.OnHTML("a.WlydOe", func(e *colly.HTMLElement) {
		storiesLink := e.Attr("href")
		storiesDesc := e.ChildText("div.mCBkyc.tNxQIb.ynAwRc.jBgGLd.OSrXXb")
		if len(storiesLink) > 0 {
			var jsonObj map[string]interface{}
			err := json.Unmarshal([]byte("{}"), &jsonObj)
			if err != nil {
				fmt.Println(err)
				return
			}
			resultIndex++
			storiesResult := &StoriesResult{
				Description: storiesDesc,
				Link:        storiesLink,
				Index:       resultIndex,
			}
			serpResults.Stories = append(serpResults.Stories, *storiesResult)
		}
	})

	// parse top 'videos section' of search results
	c.OnHTML("div.RzdJxc", func(e *colly.HTMLElement) {
		var videosHeader = e.ChildText("div.fc9yUc.tNxQIb.ynAwRc.OSrXXb")
		var videosSubheader = e.ChildText("div.FzCfme")
		var videosLink = e.ChildAttr("div.sI5x9c > a.X5OiLe:last-child", "href")
		if len(videosLink) > 0 {
			var jsonObj map[string]interface{}
			err := json.Unmarshal([]byte("{}"), &jsonObj)
			if err != nil {
				fmt.Println(err)
				return
			}
			resultIndex++
			videoResult := &VideoResult{
				Title:       videosHeader,
				Description: videosSubheader,
				Link:        videosLink,
				Index:       resultIndex,
			}
			serpResults.Videos = append(serpResults.Videos, *videoResult)

		}
	})

	// parse typical search results
	c.OnHTML("#cnt", func(e *colly.HTMLElement) {
		e.ForEach(".MjjYud", func(_ int, el *colly.HTMLElement) {
			resultIndex++
			ParseGoogleResult(el, serpResults, resultIndex)
			el.ForEach("div.d4rhi", func(_ int, elm *colly.HTMLElement) {
				resultIndex++
				ParseGoogleResult(elm, serpResults, resultIndex)
			})
		})
	})

	// parse people also ask section
	c.OnHTML("div.wQiwMc.related-question-pair div div span", func(e *colly.HTMLElement) {
		var question = e.Text
		if len(question) > 0 {
			var jsonObj map[string]interface{}
			err := json.Unmarshal([]byte("{}"), &jsonObj)
			if err != nil {
				fmt.Println(err)
				return
			}
			questionResult := &QuestionResult{
				Question: question,
			}
			serpResults.Questions = append(serpResults.Questions, *questionResult)

		}

	})

	c.OnError(func(_ *colly.Response, err error) {
		log.Println("Something went wrong:", err)
	})
	if nextPage == "" {

		q.AddURL(initialUrl)
	}

	q.Run(c)
}

func GoogleService(query string, pages string) SerpResults {
	serpResults = new(SerpResults)
	CrawlGoogle(query, pages)
	return *serpResults
}
