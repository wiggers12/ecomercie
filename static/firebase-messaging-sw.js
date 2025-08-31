// firebase-messaging-sw.js

// 🔹 Importa os scripts do Firebase compatíveis com Service Worker
importScripts("https://www.gstatic.com/firebasejs/10.12.2/firebase-app-compat.js");
importScripts("https://www.gstatic.com/firebasejs/10.12.2/firebase-messaging-compat.js");

// 🔹 Configuração do seu projeto Firebase
firebase.initializeApp({
  apiKey: "AIzaSyB-rnG4cIZzEb1w_h_qmif3XPSx28ZIdaM",
  authDomain: "ecomercie-vendas.firebaseapp.com",
  projectId: "ecomercie-vendas",
  storageBucket: "ecomercie-vendas.appspot.com",
  messagingSenderId: "1054540261609",
  appId: "1:1054540261609:web:90042b823220b4c73f6878",
  measurementId: "G-TNC5M9G89H"
});

// Inicializa o Messaging
const messaging = firebase.messaging();

// 🔔 Listener para notificações recebidas em segundo plano
messaging.onBackgroundMessage((payload) => {
  console.log("📩 [Service Worker] Notificação recebida em segundo plano:", payload);

  const notificationTitle = payload.notification?.title || "Nova Notificação";
  const notificationOptions = {
    body: payload.notification?.body || "Você recebeu uma nova mensagem",
    icon: "/icon-192.png",
    badge: "/icon-192.png",
    vibrate: [200, 100, 200]
  };

  // Exibe a notificação
  self.registration.showNotification(notificationTitle, notificationOptions);
});

// 🔔 Permite clique na notificação abrir o app
self.addEventListener("notificationclick", (event) => {
  event.notification.close();
  event.waitUntil(
    clients.matchAll({ type: "window", includeUncontrolled: true }).then((clientList) => {
      if (clientList.length > 0) {
        return clientList[0].focus();
      }
      return clients.openWindow("/");
    })
  );
});