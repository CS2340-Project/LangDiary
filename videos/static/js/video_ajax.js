document.addEventListener("DOMContentLoaded", function () {
  const csrfToken = document.querySelector("[name=csrfmiddlewaretoken]").value;

  // Favorite button functionality
  document.querySelectorAll(".toggle-favorite-btn").forEach((button) => {
    button.addEventListener("click", function () {
      const videoId = this.dataset.videoId;

      fetch("/videos/toggle-favorite/", {
        method: "POST",
        headers: {
          "Content-Type": "application/x-www-form-urlencoded",
          "X-CSRFToken": csrfToken,
        },
        body: `video_id=${videoId}`,
      })
        .then((response) => response.json())
        .then((data) => {
          if (data.status === "success") {
            // Update the button appearance
            const svg = this.querySelector("svg");

            if (data.is_favorite) {
              // Is now a favorite
              this.classList.remove("bg-slate-600", "hover:bg-slate-700");
              this.classList.add("bg-yellow-500", "hover:bg-yellow-600");
              svg.setAttribute("fill", "currentColor");

              // Remove the text if it exists
              this.textContent = "";
              this.appendChild(svg);
            } else {
              // Is no longer a favorite
              this.classList.remove("bg-yellow-500", "hover:bg-yellow-600");
              this.classList.add("bg-slate-600", "hover:bg-slate-700");
              svg.setAttribute("fill", "none");

              // Add back the text
              svg.classList.add("mr-1");
              this.appendChild(svg);
              this.appendChild(document.createTextNode("Favorite"));
            }

            // Reload the page to reflect changes in the video grid
            // For a smoother experience, you could update the DOM directly instead
            window.location.reload();
          }
        })
        .catch((error) => {
          console.error("Error toggling favorite:", error);
        });
    });
  });

  // Mark watched button functionality
  document.querySelectorAll(".mark-watched-btn").forEach((button) => {
    button.addEventListener("click", function () {
      const videoId = this.dataset.videoId;

      fetch("/videos/mark-watched/", {
        method: "POST",
        headers: {
          "Content-Type": "application/x-www-form-urlencoded",
          "X-CSRFToken": csrfToken,
        },
        body: `video_id=${videoId}`,
      })
        .then((response) => response.json())
        .then((data) => {
          if (data.status === "success") {
            // Show feedback to the user
            this.innerHTML = `
                      <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 mr-1" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
                      </svg>
                      Watched!
                  `;
            this.classList.remove("bg-slate-600", "hover:bg-slate-700");
            this.classList.add("bg-green-500", "hover:bg-green-600");

            // Reload the page after a short delay to reflect changes in the video grid
            setTimeout(() => {
              window.location.reload();
            }, 1000);
          }
        })
        .catch((error) => {
          console.error("Error marking as watched:", error);
        });
    });
  });

  // Remove button functionality
  document.querySelectorAll(".remove-btn").forEach((button) => {
    button.addEventListener("click", function () {
      if (
        !confirm(
          "Are you sure you want to remove this video from your collection?"
        )
      ) {
        return;
      }

      const videoId = this.dataset.videoId;

      fetch("/videos/remove-video/", {
        method: "POST",
        headers: {
          "Content-Type": "application/x-www-form-urlencoded",
          "X-CSRFToken": csrfToken,
        },
        body: `video_id=${videoId}`,
      })
        .then((response) => response.json())
        .then((data) => {
          if (data.status === "success") {
            // Redirect to the index page
            window.location.href = "/videos/";
          }
        })
        .catch((error) => {
          console.error("Error removing video:", error);
        });
    });
  });

  // Form submission with loading state
  const generatorForm = document.getElementById("generatorForm");
  const generateButton = document.getElementById("generateVideos");

  if (generatorForm) {
    generatorForm.addEventListener("submit", function () {
      // Disable the button and show loading state
      generateButton.disabled = true;
      generateButton.innerHTML = `
              <svg class="animate-spin h-5 w-5 mr-2" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                  <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                  <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
              Searching...
          `;
    });
  }
});
