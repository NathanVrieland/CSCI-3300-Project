package main

import (
	"encoding/json"
	"io/ioutil"
	"log"
	"net/http"
	"os"
)

type ClientMessage struct { // expected data recieved from client when message is sent
	Name    string `json:"name"`
	Message string `json:"message"`
}

func check(e error) {
	if e != nil {
		panic(e)
	}
}

// IndexHandler handles the GET request on /index and serves the homepage
func IndexHandler(w http.ResponseWriter, r *http.Request) {
	homepage, _ := os.ReadFile("index.html")  // read file and store string in variable
	log.Printf(r.RemoteAddr + " " + r.Method) // log this request
	w.Write([]byte(homepage))                 // serve the html file to the client
}

// handler for when a message is posted
func messageHandler(w http.ResponseWriter, r *http.Request) {
	log.Printf(r.RemoteAddr + " " + r.Method) // logs the ip and the type of request

	body, err := ioutil.ReadAll(r.Body) // reads the body of the post request
	check(err)

	var data ClientMessage            // used to store POST body
	err = json.Unmarshal(body, &data) // populates clientmessage object with data from request
	check(err)

	log.Printf(data.Name + ": " + data.Message)
	file, err := os.OpenFile("messages.txt", os.O_APPEND|os.O_CREATE|os.O_WRONLY, 0644)
	check(err)
	defer file.Close()
	file.WriteString(data.Name + ": " + data.Message + "\n")
}

func contentHandler(w http.ResponseWriter, r *http.Request) { // handler for GET request requesting the messages in the chat
	dat, err := os.ReadFile("messages.txt") 
	check(err)
	log.Printf(r.RemoteAddr + " " + r.Method)
	w.Write(dat)
}

func main() {
	//get the value of the ADDR environment variable
	addr := ":80"

	//if it's blank, default to ":80", which means
	//listen port 80 for requests addressed to any host
	if len(addr) == 0 {
		addr = ":80"
	}

	//create a new mux (router)
	//the mux calls different functions for
	//different resource paths
	mux := http.NewServeMux()

	//tell it to call the HelloHandler() function
	//when someone requests the resource path `/hello`
	mux.HandleFunc("/", IndexHandler)
	mux.HandleFunc("/message", messageHandler)
	mux.HandleFunc("/content", contentHandler)
	//start the web server using the mux as the root handler,
	//and report any errors that occur.
	//the ListenAndServe() function will block so
	//this program will continue to run until killed
	log.Printf("server is listening at %s...", addr)
	log.Fatal(http.ListenAndServe(addr, mux))
}
