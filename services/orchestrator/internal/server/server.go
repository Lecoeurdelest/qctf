package server

import (
	"crypto/sha256"
	"crypto/subtle"
	"encoding/json"
	"net/http"
)

func New(token string) http.Handler {
	mux := http.NewServeMux()
	mux.HandleFunc("GET /healthz", func(w http.ResponseWriter, r *http.Request) {
		respond(w, http.StatusOK, map[string]any{"status": "ok"})
	})
	mux.HandleFunc("GET /readyz", func(w http.ResponseWriter, r *http.Request) {
		respond(w, http.StatusServiceUnavailable, map[string]any{"status": "not_ready", "reason": "kctf_adapter_disabled"})
	})
	internal := http.NewServeMux()
	internal.HandleFunc("GET /internal/v1/runtime", func(w http.ResponseWriter, r *http.Request) {
		respond(w, http.StatusOK, map[string]any{
			"service": "orchestrator", "mode": "scaffold", "kctf_connected": false,
			"reconciler_enabled": false, "instance_storage": "not_implemented",
		})
	})
	internal.HandleFunc("POST /internal/v1/instances", func(w http.ResponseWriter, r *http.Request) {
		respond(w, http.StatusNotImplemented, map[string]any{"error": "durable_instance_lifecycle_not_implemented"})
	})
	mux.Handle("/internal/", authorize(token, internal))
	return mux
}

func authorize(token string, next http.Handler) http.Handler {
	expected := sha256.Sum256([]byte("Bearer " + token))
	return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		actual := sha256.Sum256([]byte(r.Header.Get("Authorization")))
		if len(token) < 32 || subtle.ConstantTimeCompare(actual[:], expected[:]) != 1 {
			respond(w, http.StatusUnauthorized, map[string]any{"error": "unauthorized"})
			return
		}
		next.ServeHTTP(w, r)
	})
}

func respond(w http.ResponseWriter, code int, body map[string]any) {
	w.Header().Set("Content-Type", "application/json")
	w.Header().Set("Cache-Control", "no-store")
	w.WriteHeader(code)
	_ = json.NewEncoder(w).Encode(body)
}
