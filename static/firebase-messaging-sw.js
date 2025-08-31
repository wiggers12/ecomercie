// firebase-messaging-sw.js

importScripts("https://www.gstatic.com/firebasejs/10.12.2/firebase-app.js");
importScripts("https://www.gstatic.com/firebasejs/10.12.2/firebase-messaging.js");

firebase.initializeApp({
  apiKey: "AIzaSyB-rnG4cIZzEb1w_h_qmif3XPSx28ZIdaM",
  authDomain: "ecomercie-vendas.firebaseapp.com",
  projectId: "ecomercie-vendas",
  storageBucket: "ecomercie-vendas.firebasestorage.app",
  messagingSenderId: "1054540261609",
  appId: "1:1054540261609:web:90042b823220b4c73f6878",
  measurementId: "G-TNC5M9G89H"
});

// Aqui NÃO se usa getMessaging, apenas firebase.messaging()
const messaging = firebase.messaging();

messaging.onBackgroundMessage((payload) => {
  console.log("[firebase-messaging-sw.js] Mensagem recebida em segundo plano:", payload);

  const notificationTitle = payload.notification.title;
  const notificationOptions = {
    body: payload.notification.body,
    icon: '/static/icon-192.png'

  };

  self.registration.showNotification(notificationTitle, notificationOptions);
});
