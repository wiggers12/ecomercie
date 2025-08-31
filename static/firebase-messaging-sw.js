// firebase-messaging-sw.js (Service Worker para push)
importScripts("https://www.gstatic.com/firebasejs/10.12.2/firebase-app-compat.js");
importScripts("https://www.gstatic.com/firebasejs/10.12.2/firebase-messaging-compat.js");

// 🔹 Configuração do Firebase
firebase.initializeApp({
  apiKey: "AIzaSyB-rnG4cIZzEb1w_h_qmif3XPSx28ZIdaM",
  authDomain: "ecomercie-vendas.firebaseapp.com",
  projectId: "ecomercie-vendas",
  storageBucket: "ecomercie-vendas.firebasestorage.app",
  messagingSenderId: "1054540261609",
  appId: "1:1054540261609:web:90042b823220b4c73f6878",
  measurementId: "G-TNC5M9G89H"
});

// 🔹 Inicializa o messaging
const messaging = firebase.messaging();

// 🔹 Captura mensagens quando o app está em segundo plano
messaging.onBackgroundMessage((payload) => {
  console.log("📩 [SW] Mensagem recebida em segundo plano:", payload);

  const notificationTitle = payload.notification?.title || "Nova Notificação";
  const notificationOptions = {
    body: payload.notification?.body || "Você recebeu uma nova atualização!",
    icon: "/icon-192.png",
    badge: "/icon-192.png",
    vibrate: [200, 100, 200], // 🔔 vibração no celular
    data: payload.data || {}
  };

  self.registration.showNotification(notificationTitle, notificationOptions);
});

// 🔹 Clique na notificação → abre o painel admin
self.addEventListener("notificationclick", function(event) {
  event.notification.close();
  event.waitUntil(
    clients.matchAll({ type: "window", includeUncontrolled: true }).then((clientList) => {
      for (const client of clientList) {
        if (client.url.includes("/admin") && "focus" in client) {
          return client.focus();
        }
      }
      if (clients.openWindow) {
        return clients.openWindow("/admin");
      }
    })
  );
});
