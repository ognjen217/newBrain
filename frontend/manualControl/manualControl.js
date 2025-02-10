// Osluškujemo događaje pritiska tastera na celoj stranici
document.addEventListener('keydown', function(event) {
  const key = event.key;
  // Dozvoljeni tasteri: W, A, S, D (bilo malo ili veliko slovo)
  if (['w', 'a', 's', 'd', 'W', 'A', 'S', 'D'].includes(key)) {
    // Šaljemo POST zahtev na backend
    fetch('/manual-control', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ key: key })
    })
    .then(response => response.json())
    .then(data => console.log('Komanda poslata:', data))
    .catch(error => console.error('Greška pri slanju komande:', error));
  }
});
