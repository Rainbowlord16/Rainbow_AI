(() => {
  "use strict";
  const page = (location.pathname.split("/").pop() || "homepage.html").toLowerCase();
  const pages = [
    {file:"homepage.html",label:"Home",key:"home"},
    {file:"index.html",label:"AI Workspace",key:"ai"},
    {file:"languagebook.html",label:"Language",key:"language"},
    {file:"calculator.html",label:"Calculator",key:"calculator"}
  ];
  const bar = document.createElement("nav");
  bar.className = "rw-ecosystem-bar";
  bar.setAttribute("aria-label","Rainbow ecosystem navigation");
  const brand = document.createElement("a");
  brand.className = "rw-ecosystem-brand";
  brand.href = "homepage.html";
  brand.innerHTML = '<span class="rw-ecosystem-mark" aria-hidden="true"></span><span>RAINBOW</span>';
  bar.appendChild(brand);
  pages.forEach(item => {
    const link = document.createElement("a");
    link.className = "rw-ecosystem-link";
    link.dataset.rwLink = item.key;
    link.href = item.file;
    link.textContent = item.label;
    if (page === item.file) link.setAttribute("aria-current","page");
    bar.appendChild(link);
  });
  const ask = document.createElement("button");
  ask.className = "rw-ecosystem-ai";
  ask.type = "button";
  ask.textContent = "✦ Ask Rainbow";
  ask.addEventListener("click", () => {
    let context = "I opened the Rainbow ecosystem from " + (document.title || page) + ". Help me with this page.";
    if (page === "calculator.html") {
      const display = document.getElementById("display");
      const history = document.getElementById("history");
      context += "\nCurrent calculator display: " + (display?.value || "0") + ".\nRecent calculations: " + (history?.innerText || "None yet").slice(-1200);
    } else if (page === "languagebook.html") {
      const course = document.getElementById("headerCourseName")?.textContent?.trim();
      const level = document.getElementById("headerCourseLevel")?.textContent?.trim();
      const question = document.getElementById("quizQuestion")?.textContent?.trim();
      context += "\nCurrent course: " + (course || "Not selected") + ". Level: " + (level || "Not specified") + ". Current lesson/question: " + (question || "Dashboard") + ". Help me learn, practise, translate, or understand this material.";
    } else if (page === "homepage.html") {
      context += "\nGive me a guided tour of the available Rainbow tools.";
    }
    window.RainbowBridge.openAI(context, page);
  });
  bar.appendChild(ask);
  document.addEventListener("DOMContentLoaded", () => {
    document.body.dataset.rwPage = page.replace(/\.html$/, "");
    document.body.appendChild(bar);
  });
  window.RainbowBridge = {
    openAI(prompt, source) {
      const payload = {prompt:String(prompt || "Help me with Rainbow AI."),source:String(source || page),createdAt:Date.now()};
      try {
        localStorage.setItem("rainbow:handoff:v1",JSON.stringify(payload));
        location.href = "index.html?handoff=1";
      } catch (error) {
        const status = document.createElement("div");
        status.className = "rw-ecosystem-status";
        status.setAttribute("role","alert");
        status.textContent = "Could not prepare the AI handoff. Please allow site storage and try again.";
        document.body.appendChild(status);
      }
    }
  };
})();