$(document).ready(function () {
  let timeout;
  let isTyping = false;

  $("#search-bar").on("keydown", function (e) {
    // Block Enter (keyCode 13) and Tab (keyCode 9)
    if (e.key === "Enter" || e.key === "Tab") {
      e.preventDefault();
    }
  });

  $("#search-bar").on("keyup", function () {
    clearTimeout(timeout)
    const $this = $(this)
    const el = $this[0]
    const text = el.textContent
  
    if (!isTyping) isTyping = true
  
    if (text.trim()) {
      const savedRange = saveSelection(el)
  
      timeout = setTimeout(() => {
        const words = text.split(/\s+/)
        let modified = text
  
        const promises = words.map((word) =>
          $.ajax({
            url: "/spellcheck",
            method: "POST",
            contentType: "application/json",
            data: JSON.stringify({ word }),
          }).then((response) => {
            if (!response.is_correct) {
              const escapedWord = word.replace(/[-\/\\^$*+?.()|[\]{}]/g, "\\$&")
              const span = `<span class="misspelled" data-word="${word}" title="${response.suggestions?.join(", ") || "No suggestions"}">${word}</span>`
              const regex = new RegExp(`\\b${escapedWord}\\b`, "g")
              modified = modified.replace(regex, span)
            }
          })
        )
  
        Promise.all(promises).then(() => {
          if (el.innerHTML !== modified) {
            el.innerHTML = modified
            restoreSelection(el, savedRange)
          }
        })
      }, 500)
    } else {
      isTyping = false
    }
  })
  
  // Save and restore caret range (not just position)
  function saveSelection(containerEl) {
    const sel = window.getSelection()
    if (sel.rangeCount === 0) return null
    const range = sel.getRangeAt(0)
    const preSelectionRange = range.cloneRange()
    preSelectionRange.selectNodeContents(containerEl)
    preSelectionRange.setEnd(range.startContainer, range.startOffset)
    const start = preSelectionRange.toString().length
  
    return { start, end: start + range.toString().length }
  }
  
  function restoreSelection(containerEl, savedSel) {
    if (!savedSel) return
    const charIndex = { count: 0 }
    const range = document.createRange()
    range.setStart(containerEl, 0)
    range.collapse(true)
  
    let nodeStack = [containerEl], node, foundStart = false, stop = false
  
    while (!stop && (node = nodeStack.pop())) {
      if (node.nodeType === 3) {
        const nextCharIndex = charIndex.count + node.length
        if (!foundStart && savedSel.start >= charIndex.count && savedSel.start <= nextCharIndex) {
          range.setStart(node, savedSel.start - charIndex.count)
          foundStart = true
        }
        if (foundStart && savedSel.end >= charIndex.count && savedSel.end <= nextCharIndex) {
          range.setEnd(node, savedSel.end - charIndex.count)
          stop = true
        }
        charIndex.count = nextCharIndex
      } else {
        let i = node.childNodes.length
        while (i--) nodeStack.push(node.childNodes[i])
      }
    }
  
    const sel = window.getSelection()
    sel.removeAllRanges()
    sel.addRange(range)
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
          confirmButtonColor: "#3085d6", // Preview button color
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

function confirmDelete(userId) {
  Swal.fire({
      title: 'Are you sure?',
      text: "This will mark the user as deleted.",
      icon: 'warning',
      showCancelButton: true,
      confirmButtonColor: '#d33',
      cancelButtonColor: '#3085d6',
      confirmButtonText: 'Yes, delete it!',
      reverseButtons: true
  }).then((result) => {
      if (result.isConfirmed) {
          document.getElementById('delete-form-' + userId).submit();
      }
  });
}