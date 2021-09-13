FROM envoyproxy/envoy-alpine:v1.18-latest
ADD ./build/envoy/conf.d/envoy.yaml /etc/envoy/envoy.yaml
CMD /usr/local/bin/envoy -c /etc/envoy/envoy.yaml
EXPOSE 8081