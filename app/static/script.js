// Open the Add Post Modal
document.getElementById('open-add-modal').addEventListener('click', function () {
    document.getElementById('add-modal').style.display = 'block';
  });
  
  // Close the Add Post Modal
  document.getElementById('close-add-modal').addEventListener('click', function () {
    document.getElementById('add-modal').style.display = 'none';
  });

  function showFullSize(fullSizeUrl) {
      window.open(fullSizeUrl, '_blank');
  }