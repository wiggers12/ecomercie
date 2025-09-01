// --- Importa Firebase compat ---
importScripts("https://www.gstatic.com/firebasejs/10.12.2/firebase-app-compat.js");
importScripts("https://www.gstatic.com/firebasejs/10.12.2/firebase-messaging-compat.js");

// --- Configuração Firebase ---
firebase.initializeApp({
  apiKey: "AIzaSyB-rnG4cIZzEb1w_h_qmif3XPSx28ZIdaM",
  authDomain: "ecomercie-vendas.firebaseapp.com",
  projectId: "ecomercie-vendas",
  storageBucket: "ecomercie-vendas.firebasestorage.app",
  messagingSenderId: "1054540261609",
  appId: "1:1054540261609:web:90042b823220b4c73f6878",
  measurementId: "G-TNC5M9G89H"
});

const messaging = firebase.messaging();

// --- Mensagens em segundo plano ---
messaging.onBackgroundMessage((payload) => {
  console.log("📩 [SW] Mensagem recebida:", payload);

  const notificationTitle = payload.notification?.title || payload.data?.title || "Nova Notificação";
  const notificationOptions = {
    body: payload.notification?.body || payload.data?.body || "Você recebeu uma nova mensagem",
    icon: "/icon-192.png",
    badge: "/icon-192.png",
    data: { url: payload.data?.url || "/admin" }
  };

  self.registration.showNotification(notificationTitle, notificationOptions);
});

// --- Clique na notificação ---
self.addEventListener("notificationclick", (event) => {
  console.log("🖱️ [SW] Notificação clicada:", event);
  event.notification.close();

  event.waitUntil(
    clients.matchAll({ type: "window", includeUncontrolled: true }).then((clientList) => {
      for (const client of clientList) {
        if (client.url.includes("/admin") && "focus" in client) {
          return client.focus();
        }
      }
      if (clients.openWindow) {
        return clients.openWindow(event.notification.data.url || "/admin");
      }
    })
  );
});

// --- Cache PWA ---
const CACHE_NAME = "ecomercie-cache-v1";
const ASSETS = ["/", "/manifest.json", "/icon-192.png", "/icon-512.png"];

self.addEventListener("install", (event) => {
  console.log("✅ [SW] Instalado");
  event.waitUntil(
    caches.open(CACHE_NAME).then((cache) => {
      return cache.addAll(ASSETS);
    })
  );
});

self.addEventListener("activate", (event) => {
  console.log("🚀 [SW] Ativo");
  event.waitUntil(
    caches.keys().then((keys) =>
      Promise.all(keys.filter((k) => k !== CACHE_NAME).map((k) => caches.delete(k)))
    )
  );
});

self.addEventListener("fetch", (event) => {
  event.respondWith(
    caches.match(event.request).then((resp) => resp || fetch(event.request))
  );
});
