window.sendEvent = (action, data) => {
  eventBody = {
    url: window.location.href,
    action: action,
    details: { ...data },
  };
  console.log(eventBody);
};

window.onload = () => {
  sendEvent("load", null);
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
