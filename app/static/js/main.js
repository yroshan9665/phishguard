// Auto-dismiss alerts after 5 seconds
document.querySelectorAll('.alert.alert-dismissible').forEach(alert => {
  setTimeout(() => bootstrap.Alert.getOrCreateInstance(alert).close(), 5000);
});
