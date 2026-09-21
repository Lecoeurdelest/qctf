package server

import (
	"encoding/json"
	"net/http/httptest"
	"strings"
	"testing"
)

func TestScaffoldContract(t *testing.T) {
	token := strings.Repeat("a", 64)
	for _, tc := range []struct {
		name, method, path, auth string
		status                   int
	}{
		{"live", "GET", "/healthz", "", 200},
		{"not_ready", "GET", "/readyz", "", 503},
		{"missing_auth", "GET", "/internal/v1/runtime", "", 401},
		{"wrong_auth", "GET", "/internal/v1/runtime", "Bearer wrong", 401},
		{"wrong_scheme", "GET", "/internal/v1/runtime", "Token " + token, 401},
		{"runtime", "GET", "/internal/v1/runtime", "Bearer " + token, 200},
		{"no_fake_instance", "POST", "/internal/v1/instances", "Bearer " + token, 501},
	} {
		t.Run(tc.name, func(t *testing.T) {
			r := httptest.NewRequest(tc.method, tc.path, nil)
			r.Header.Set("Authorization", tc.auth)
			w := httptest.NewRecorder()
			New(token).ServeHTTP(w, r)
			if w.Code != tc.status {
				t.Fatalf("status = %d; want %d", w.Code, tc.status)
			}
			var body map[string]any
			if err := json.Unmarshal(w.Body.Bytes(), &body); err != nil {
				t.Fatal(err)
			}
			if tc.name == "runtime" && body["kctf_connected"] != false {
				t.Fatal("scaffold must not report a connected cluster")
			}
		})
	}
}

func TestEmptySecretFailsClosed(t *testing.T) {
	r := httptest.NewRequest("GET", "/internal/v1/runtime", nil)
	r.Header.Set("Authorization", "Bearer ")
	w := httptest.NewRecorder()
	New("").ServeHTTP(w, r)
	if w.Code != 401 {
		t.Fatalf("empty secret authorized: %d", w.Code)
	}
}
