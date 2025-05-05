$(document).ready(function () {
    let timeout;
    let isTyping = false;
    
    $("#search-bar").on("input", function () {
      clearTimeout(timeout);
      const $this = $(this);
      const text = $this.text();
    
      // Check if typing has started
      if (!isTyping) {
        isTyping = true;
      }
    
      if (text.trim()) {
        // Only trigger after typing stops
        timeout = setTimeout(() => {
          const words = text.split(/\s+/);
          let modified = text;
    
          const promises = words.map((word) => {
            return $.ajax({
              url: "/spellcheck",
              method: "POST",
              contentType: "application/json",
              data: JSON.stringify({ word }),
            }).then((response) => {
              if (!response.is_correct) {
                const escapedWord = word.replace(
                  /[-\/\\^$*+?.()|[\]{}]/g,
                  "\\$&"
                );
                const span = `<span class="misspelled" data-word="${word}" title="${
                  response.suggestions?.join(", ") || "No suggestions"
                }">${word}</span>`;
                const regex = new RegExp(`\\b${escapedWord}\\b`, "g");
                modified = modified.replace(regex, span);
              }
            });
          });
    
          Promise.all(promises).then(() => {
            // Only save and restore the cursor if content actually changed
            if ($this.html() !== modified) {
              const cursorPosition = saveCaretPosition($this[0]);
    
              // Update the content
              $this.html(modified);
    
              // Restore the cursor position to the end
              restoreCaretPositionToEnd($this[0]);
            }
          });
        }, 2000);
      } else {
        // If no text, reset typing status
        isTyping = false;
      }
    });
    
    // Function to save the caret position
    function saveCaretPosition(element) {
      let caretPos = 0;
      if (document.selection) {
        element.focus();
        const range = document.selection.createRange();
        range.moveStart("character", -element.innerText.length);
        caretPos = range.text.length;
      } else if (element.selectionStart || element.selectionStart === "0") {
        caretPos = element.selectionStart;
      }
      return caretPos;
    }
    
    // Function to restore the caret position to the end
    function restoreCaretPositionToEnd(element) {
      element.focus();
      const range = document.createRange();
      const selection = window.getSelection();
      range.selectNodeContents(element);
      range.collapse(false); // Collapse the range to the end (false)
      selection.removeAllRanges();
      selection.addRange(range);
    }
    

  // Context menu for misspelled words
  $(document).on("contextmenu", ".misspelled", function (e) {
    e.preventDefault();
    const word = $(this).data("word");
    $.ajax({
      url: "/spellcheck",
      method: "POST",
      contentType: "application/json",
      data: JSON.stringify({ word }),
      success: function (response) {
        const suggestions = response.suggestions || [];
        let html = suggestions.length
          ? suggestions
              .map(
                (s) =>
                  `<li><a class="suggestion cursor-pointer" data-word="${word}" data-suggestion="${s}">${s}</a></li>`
              )
              .join("")
          : "<li>No suggestions</li>";

        html += `<li><hr></li></li><li><a class="add-to-dictionary cursor-pointer" data-word="${word}" onclick="addToDictionary('${word}')">Add to dictionary</a></li>`;

        $("#context-menu ul").html(html);
        $("#context-menu")
          .css({
            top: e.pageY,
            left: e.pageX,
          })
          .show();
      },
    });
  });

  // Other event handlers for suggestions, adding to dictionary, etc.
  $(document).on("mouseover", ".misspelled", function () {
    const word = $(this).data("word");
    const title = $(this).attr("title");
    $(this).attr("title", title); // Tooltip on hover with suggestions
  });

  $(document).on("click", ".suggestion", function (e) {
    e.preventDefault();
    const word = $(this).data("word");
    const suggestion = $(this).data("suggestion");

    // Replace misspelled word with the suggestion
    $(`.misspelled[data-word="${word}"]`).each(function () {
      const text = $(this).text();
      if (text === word) {
        $(this).replaceWith(suggestion);
        return false; // replace only first match
      }
    });

    $("#context-menu").hide();
  });

  $(document).on("click", ".add-to-dictionary", function (e) {
    e.preventDefault();
    const word = $(this).data("word");

    $.ajax({
      url: "/add-to-dictionary",
      method: "POST",
      contentType: "application/json",
      data: JSON.stringify({ word }),
      success: function (response) {
        if (response.status === "success") {
          Swal.fire({
            icon: "success",
            text: `Word "${word}" added to dictionary.`,
            toast: true,
            position: "top-end",
            showConfirmButton: false,
            timer: 3000,
          });

          $("#search-bar").html(function (_, html) {
            const regex = new RegExp(
              `<span[^>]*data-word="${word}"[^>]*>${word}</span>`,
              "g"
            );
            return html.replace(regex, word);
          });
        } else {
          Swal.fire({
            icon: "error",
            text: response.error || "Failed to add word.",
            toast: true,
            position: "top-end",
            showConfirmButton: false,
            timer: 3000,
          });
        }
      },
    });

    $("#context-menu").hide();
  });

  $(document).click(function (e) {
    if (!$(e.target).closest(".misspelled, #context-menu").length) {
      $("#context-menu").hide();
    }
  });

  $("form").on("submit", function () {
    const plainText = $("#search-bar").text().trim();
    $("#search-query").val(plainText);
  });
});

// function addToDictionary(word) {
//   fetch("/add-to-dictionary", {
//     method: "POST",
//     headers: {
//       "Content-Type": "application/json",
//     },
//     body: JSON.stringify({ word }),
//   })
//     .then((response) => response.json())
//     .then((data) => {
//       console.log(data);
//       if (data.status === "success") {
//         alert(`'${word}' added to your dictionary!`);
//       } else {
//         alert(data.message || "Failed to add word.");
//       }
//     })
//     .catch((error) => {
//       console.error("Error adding word:", error);
//     });
// }

function addToDictionary(word) {
  fetch("/add-to-dictionary", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ word }),
  })
    .then((response) => response.json())
    .then((data) => {
      console.log(data);
      if (data.status === "success") {
        alert(`'${word}' added to your dictionary!`);
      } else {
        alert(data.message || "Failed to add word.");
      }
    })
    .catch((error) => {
      console.error("Error adding word:", error);
    });
}

function showPreview(doc_id) {
  $.ajax({
    url: `/preview/${doc_id}`,
    method: "GET",
    success: function (response) {
      if (response.error) {
        Swal.fire({
          icon: "error",
          text: response.error,
          toast: true,
          position: "top-end",
          showConfirmButton: false,
          timer: 3000,
        });
      } else {
        Swal.fire({
          title: response.filename,
          text: response.content,
          icon: "info",
          showConfirmButton: true,
          width: "600px",
        });
      }
    },
    error: function () {
      Swal.fire({
        icon: "error",
        text: "Failed to load preview.",
        toast: true,
        position: "top-end",
        showConfirmButton: false,
        timer: 3000,
      });
    },
  });
}
