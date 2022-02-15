window.sendEvent = (event_type, data) => {
  eventBody = {
    event_type: event_type,
    from_url: window.location.href,
    details: { ...data },
  };
  console.log(eventBody);
  fetch("https://<api-id>.execute-api.eu-west-1.amazonaws.com/prod/events", {
    headers: { "content-type": "application/json" },
    method: "POST",
    body: JSON.stringify(eventBody),
  });
};

window.onload = () => {
  sendEvent("page_load", {});
};

document.addEventListener(
  "click",
  (event) => {
    const elementsToTrack = ["img", "button", "a", "em", "div"];
    if (!elementsToTrack.includes(event.target.localName)) return;

    data = {
      element: event.target.localName,
      id: event.target.id,
      class: event.target.className,
      innerText: event.target.innerText,
    };
    window.sendEvent("click", data);
  },
  false
);
