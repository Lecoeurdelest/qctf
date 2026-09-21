package main

import (
	"context"
	"errors"
	"log/slog"
	"net/http"
	"os"
	"os/signal"
	"syscall"
	"time"

	"qctf/services/orchestrator/internal/server"
)

func main() {
	token := os.Getenv("ORCHESTRATOR_TOKEN")
	if len(token) < 32 {
		slog.Error("ORCHESTRATOR_TOKEN must contain at least 32 characters")
		os.Exit(1)
	}
	addr := os.Getenv("LISTEN_ADDR")
	if addr == "" {
		addr = ":8081"
	}
	service := &http.Server{
		Addr: addr, Handler: server.New(token),
		ReadHeaderTimeout: 5 * time.Second, ReadTimeout: 10 * time.Second,
		WriteTimeout: 10 * time.Second, IdleTimeout: 60 * time.Second,
		MaxHeaderBytes: 16 << 10,
	}
	ctx, stop := signal.NotifyContext(context.Background(), syscall.SIGINT, syscall.SIGTERM)
	defer stop()
	go func() {
		<-ctx.Done()
		deadline, cancel := context.WithTimeout(context.Background(), 10*time.Second)
		defer cancel()
		if err := service.Shutdown(deadline); err != nil {
			slog.Error("shutdown failed", "error", err)
		}
	}()
	slog.Info("orchestrator listening; Kubernetes adapter is disabled", "address", addr)
	if err := service.ListenAndServe(); err != nil && !errors.Is(err, http.ErrServerClosed) {
		slog.Error("server failed", "error", err)
		os.Exit(1)
	}
}
