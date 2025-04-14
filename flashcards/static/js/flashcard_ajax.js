document.addEventListener("DOMContentLoaded", function () {
  console.log("Flashcard script loaded");

  // Basic event handlers for navigation
  const prevButton = document.querySelector(".prev-card-btn");
  const nextButton = document.querySelector(".next-card-btn");
  const flipButton = document.querySelector(".flip-card-btn");
  const cardBox = document.querySelector(".card-box");
  const cardContent = document.querySelector(".card-content");

  // Load card content directly from the API on page load
  if (cardBox && cardContent) {
    const cardId = cardBox.getAttribute("data-card-id");
    const isBackSide =
      cardBox.classList.contains("back-side") ||
      window.location.href.includes("side=back");

    if (cardId) {
      console.log("Loading card content for ID:", cardId);

      // Show loading message
      cardContent.textContent = "Loading card content...";

      // Fetch card data
      fetch(`/flashcards/api/card/${cardId}/`)
        .then((response) => {
          if (!response.ok) {
            throw new Error("Network response was not ok");
          }
          return response.json();
        })
        .then((data) => {
          console.log("Card data loaded:", data);

          // Update content based on side
          if (isBackSide) {
            cardContent.textContent =
              data.back_text || "No back content available";
          } else {
            cardContent.textContent =
              data.front_text || "No front content available";
          }
        })
        .catch((error) => {
          console.error("Error loading card data:", error);
          cardContent.textContent =
            "Error loading card content. Please refresh the page.";
        });
    } else {
      cardContent.textContent = "No card ID found. Please try another card.";
    }
  }

  // Simple navigation - use direct links
  if (prevButton) {
    prevButton.addEventListener("click", function (e) {
      // Don't prevent default - let the link work normally
      console.log("Previous button clicked");
    });
  }

  if (nextButton) {
    nextButton.addEventListener("click", function (e) {
      // Don't prevent default - let the link work normally
      console.log("Next button clicked");
    });
  }

  // Implement flip functionality
  if (flipButton) {
    flipButton.addEventListener("click", function (e) {
      e.preventDefault();
      console.log("Flip button clicked");

      const cardId = cardBox.getAttribute("data-card-id");
      const isShowingBack = cardBox.classList.contains("back-side");

      // Just redirect to the same card with the opposite side
      window.location.href = `/flashcards/?card_id=${cardId}${
        isShowingBack ? "" : "&side=back"
      }`;
    });
  }

  // Handle review button
  const reviewButton = document.querySelector(".mark-reviewed-btn");
  if (reviewButton) {
    reviewButton.addEventListener("click", function (e) {
      e.preventDefault();
      const cardId = this.getAttribute("data-card-id");
      if (cardId) {
        const csrfToken = document.querySelector(
          "[name=csrfmiddlewaretoken]"
        )?.value;

        fetch("/flashcards/api/mark-reviewed/", {
          method: "POST",
          headers: {
            "Content-Type": "application/x-www-form-urlencoded",
            "X-CSRFToken": csrfToken,
          },
          body: `card_id=${cardId}`,
        })
          .then((response) => response.json())
          .then((data) => {
            if (data.success) {
              // Just reload the page to show updated revision count
              window.location.reload();
            }
          })
          .catch((error) => {
            console.error("Error marking as reviewed:", error);
            alert("Error marking card as reviewed");
          });
      }
    });
  }

  // Handle delete button
  const deleteButton = document.querySelector(".delete-card-btn");
  if (deleteButton) {
    deleteButton.addEventListener("click", function (e) {
      e.preventDefault();
      const cardId = this.getAttribute("data-card-id");
      if (cardId && confirm("Are you sure you want to delete this card?")) {
        const csrfToken = document.querySelector(
          "[name=csrfmiddlewaretoken]"
        )?.value;

        fetch("/flashcards/api/delete/", {
          method: "POST",
          headers: {
            "Content-Type": "application/x-www-form-urlencoded",
            "X-CSRFToken": csrfToken,
          },
          body: `card_id=${cardId}`,
        })
          .then((response) => response.json())
          .then((data) => {
            if (data.success) {
              // Navigate to next card or reload
              if (data.next_id) {
                window.location.href = `/flashcards/?card_id=${data.next_id}`;
              } else if (data.prev_id) {
                window.location.href = `/flashcards/?card_id=${data.prev_id}`;
              } else {
                window.location.reload();
              }
            }
          })
          .catch((error) => {
            console.error("Error deleting card:", error);
            alert("Error deleting card");
          });
      }
    });
  }
});
