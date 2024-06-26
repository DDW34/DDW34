$(document).ready(function () {
  // Smooth scrolling for navigation links and back to top button
  $(".navbar a, footer a[href='#halamanku']").on("click", function (event) {
    if (this.hash !== "") {
      event.preventDefault();
      var hash = this.hash;
      $("html, body").animate(
        {
          scrollTop: $(hash).offset().top,
        },
        900,
        function () {
          window.location.hash = hash;
        }
      );
    }
  });

  // Back to top button
  var backToTopButton = $("#back-to-top");

  $(window).scroll(function () {
    if ($(this).scrollTop() > 100) {
      backToTopButton.fadeIn();
    } else {
      backToTopButton.fadeOut();
    }
  });

  backToTopButton.on("click", function () {
    $("html, body").animate({ scrollTop: 0 }, 800);
    return false;
  });

  // Trigger animation on scroll
  $(window).scroll(function () {
    $(".slideanim").each(function () {
      var pos = $(this).offset().top;
      var winTop = $(window).scrollTop();
      if (pos < winTop + 600) {
        $(this).addClass("slide");
      }
    });
  });

  // Fungsi untuk memulai kamera
  function startCamera() {
    const cameraFeed = document.getElementById("camera-feed");
    cameraFeed.style.display = "block";
    cameraFeed.src = "/video_feed"; // Updated URL for video feed
  }

  // Fungsi untuk mematikan kamera
  function offCamera() {
    const cameraFeed = document.getElementById("camera-feed");
    cameraFeed.style.display = "none";
    cameraFeed.src = "";
  }

  // Fungsi untuk mengunggah file dan mengirimkan form data ke Flask
  function uploadFile() {
    const form = document.getElementById("upload-form");
    const formData = new FormData(form);

    fetch("/", {
      method: "POST",
      body: formData,
    })
      .then((response) => response.json())
      .then((data) => {
        // Handle response data (jika perlu)
        console.log(data);
      })
      .catch((error) => {
        console.error("Error:", error);
      });
  }

  // Fungsi untuk menampilkan deskripsi hasil deteksi
  function displayDescriptions(descriptions) {
    const descriptionContainer = document.getElementById(
      "description-container"
    );
    descriptionContainer.innerHTML = ""; // Bersihkan konten sebelumnya

    descriptions.forEach(([class_name, description]) => {
      const descriptionElement = document.createElement("div");
      descriptionElement.classList.add("description");
      descriptionElement.innerHTML = `<strong>${class_name}:</strong> ${description}`;
      descriptionContainer.appendChild(descriptionElement);
    });
  }

  // Event listener untuk tombol mulai kamera
  document
    .getElementById("start-camera")
    .addEventListener("click", function () {
      startCamera();
    });

  // Event listener untuk tombol matikan kamera
  document.getElementById("off-camera").addEventListener("click", function () {
    offCamera();
  });

  // Event listener untuk tombol unggah file
  document
    .getElementById("upload-button")
    .addEventListener("click", function () {
      uploadFile();
    });
});
