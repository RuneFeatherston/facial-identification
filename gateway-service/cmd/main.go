package main

import (
	"fmt"
	"log"
	"net/http"
)

func healthHandler(w http.ResponseWriter, r *http.Request) {
	w.Header().Set("Content-Type", "application/json")
	w.WriteHeader(http.StatusOK)
	fmt.Fprint(w, `{"status":"healthy"}`)
}

func main() {
	http.HandleFunc("/health", healthHandler)

	fmt.Println("Gateway service starting on :8080")
	log.Fatal(http.ListenAndServe(":8080", nil))
}
