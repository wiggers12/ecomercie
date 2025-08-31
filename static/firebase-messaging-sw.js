// firebase-messaging-sw.js

importScripts("https://www.gstatic.com/firebasejs/10.12.2/firebase-app-compat.js");
importScripts("https://www.gstatic.com/firebasejs/10.12.2/firebase-messaging-compat.js");

firebase.initializeApp({
  apiKey: "AIzaSyB-rnG4cIZzEb1w_h_qmif3XPSx28ZIdaM",
  authDomain: "ecomercie-vendas.firebaseapp.com",
  projectId: "ecomercie-vendas",
  storageBucket: "ecomercie-vendas.firebasestorage.app",
  messagingSenderId: "1054540261609",
  appId: "1:1054540261609:web:90042b823220b4c73f6878",
  measurementId: "G-TNC5M9G89H"
});

// Inicializa o Messaging
const messaging = firebase.messaging();

// 👉 Listener para mensagens em segundo plano (Android/Chrome)
messaging.onBackgroundMessage(function(payload) {
  console.log("📩 [SW] Mensagem recebida em segundo plano:", payload);

  const notificationTitle = payload.notification?.title || "Nova Notificação";
  const notificationOptions = {
    body: payload.notification?.body || "Você recebeu uma nova mensagem",
    icon: "/icon-192.png",
    badge: "/icon-192.png" // ícone pequeno no iOS
  };

  self.registration.showNotification(notificationTitle, notificationOptions);
});

// 👉 Listener extra para compatibilidade com iOS (Safari PWA ≥16.4)
self.addEventListener("push", function(event) {
  console.log("📩 [SW] Evento push capturado:", event);

  let data = {};
  if (event.data) {
    try {
      data = event.data.json();
    } catch (e) {
      console.error("Erro ao processar push:", e);
    }
  }

  const notificationTitle = data?.notification?.title || "Nova Notificação";
  const notificationOptions = {
    body: data?.notification?.body || "Você recebeu uma nova mensagem",
    icon: "/icon-192.png",
    badge: "/icon-192.png"
  };

  event.waitUntil(
    self.registration.showNotification(notificationTitle, notificationOptions)
  );
});

// 👉 Evento de clique na notificação (abrir app)
self.addEventListener("notificationclick", function(event) {
  event.notification.close();
  event.waitUntil(
    clients.matchAll({ type: "window", includeUncontrolled: true }).then(function(clientList) {
      if (clientList.length > 0) {
        return clientList[0].focus();
      }
      return clients.openWindow("/");
    })
  );
});