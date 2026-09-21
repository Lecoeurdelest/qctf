FROM golang:1.27.1-alpine AS build
WORKDIR /src
COPY go.mod ./
COPY cmd ./cmd
COPY internal ./internal
RUN CGO_ENABLED=0 go build -trimpath -ldflags="-s -w" -o /out/orchestrator ./cmd/orchestrator

FROM scratch
COPY --from=build /out/orchestrator /orchestrator
USER 65532:65532
EXPOSE 8081
ENTRYPOINT ["/orchestrator"]
