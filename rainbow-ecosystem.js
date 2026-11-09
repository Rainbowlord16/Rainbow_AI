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
  const mark = document.createElement("span");
  mark.className = "rw-ecosystem-mark";
  mark.setAttribute("aria-hidden","true");
  const brandName = document.createElement("span");
  brandName.textContent = "RAINBOW";
  brand.append(mark,brandName);
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
  ask.addEventListener("click", () => window.RainbowBridge.openAI(buildPageContext("general"), page));
  bar.appendChild(ask);

  function cleanText(node, limit=6000) {
    return String(node?.innerText || node?.textContent || "").replace(/\s+/g," ").trim().slice(0,limit);
  }
  function languageContext() {
    return {
      course: cleanText(document.getElementById("headerCourseName")) || "Current course",
      level: cleanText(document.getElementById("headerCourseLevel")) || "Not specified",
      question: cleanText(document.getElementById("quizQuestion")) || "No active question",
      lesson: cleanText(document.getElementById("lessonsInstructionContainer"),5000),
      selected: cleanText(window.getSelection?.()?.toString(),1500)
    };
  }
  function buildPageContext(action) {
    if (page === "calculator.html") {
      const expression = document.getElementById("display")?.value || "0";
      const history = cleanText(document.getElementById("history"),1400);
      const instructions = action === "similar"
        ? "Create three similar practice problems, then provide a separate answer key with clear worked solutions."
        : "Solve this expression carefully. Show the order of operations and every meaningful step, verify the result, and explain any domain or rounding assumptions.";
      return "I am using Rainbow Calculator. " + instructions + "\nExpression: " + expression + "\nRecent calculation history: " + (history || "None");
    }
    if (page === "languagebook.html") {
      const c = languageContext();
      const common = "Course: " + c.course + "; level: " + c.level + "; current question: " + c.question + "; lesson material: " + (c.lesson || "No lesson material currently visible") + "; selected text: " + (c.selected || "None");
      const prompts = {
        explain: "Act as my patient language tutor. Explain the current question and underlying grammar/vocabulary in simple steps. Give examples and common mistakes. Do not invent course facts.\n" + common,
        tutorial: "Create a structured, beginner-friendly tutorial from the visible lesson material. Include learning goals, explanation, examples, a short recap, and a mini exercise with answers at the end. If material is missing, clearly say what you need.\n" + common,
        practice: "Create five level-appropriate practice questions based on the current course and visible lesson. Mix question types, then put the answer key and explanations after the questions.\n" + common,
        translate: "Help me understand and translate the selected text in the context of my current language course. Explain important words, grammar, pronunciation guidance, and a natural example.\n" + common
      };
      return prompts[action] || ("Help me learn this material as a patient language tutor.\n" + common);
    }
    if (page === "homepage.html") return "Give me a guided tour of Rainbow AI, then suggest a learning or building path using the tools available in this project.";
    return "Help me with this Rainbow project page.";
  }
  function makeButton(label, action, source) {
    const button = document.createElement("button");
    button.type = "button";
    button.className = "rw-ai-tool-btn";
    button.textContent = label;
    button.addEventListener("click", () => window.RainbowBridge.openAI(buildPageContext(action), source));
    return button;
  }
  function addActionDock() {
    if (page === "languagebook.html") {
      const main = document.querySelector(".main");
      const topbar = main?.querySelector(".topbar");
      if (!main || !topbar || document.getElementById("rwLanguageAiDock")) return;
      const dock = document.createElement("section");
      dock.id = "rwLanguageAiDock";
      dock.className = "rw-ai-page-tools";
      dock.setAttribute("aria-label","Rainbow AI learning assistant");
      const heading = document.createElement("div");
      heading.className = "rw-ai-tools-heading";
      const title = document.createElement("strong");
      title.textContent = "Rainbow AI Study Coach";
      const sub = document.createElement("span");
      sub.textContent = "Explain lessons, build tutorials, and practise with AI";
      heading.append(title,sub);
      const row = document.createElement("div");
      row.className = "rw-ai-tools-actions";
      row.append(
        makeButton("Explain this question","explain","languagebook.html"),
        makeButton("Generate a tutorial","tutorial","languagebook.html"),
        makeButton("Create practice questions","practice","languagebook.html"),
        makeButton("Explain selected text","translate","languagebook.html")
      );
      dock.append(heading,row);
      topbar.insertAdjacentElement("afterend",dock);
    }
    if (page === "calculator.html") {
      const calculator = document.querySelector(".calculator");
      const display = document.getElementById("display");
      if (!calculator || !display || document.getElementById("rwCalculatorAiDock")) return;
      const dock = document.createElement("section");
      dock.id = "rwCalculatorAiDock";
      dock.className = "rw-ai-page-tools rw-ai-calculator-tools";
      dock.setAttribute("aria-label","Rainbow AI problem solving");
      const heading = document.createElement("div");
      heading.className = "rw-ai-tools-heading";
      const title = document.createElement("strong");
      title.textContent = "Solve with Rainbow AI";
      const sub = document.createElement("span");
      sub.textContent = "Get a worked solution or generate similar problems";
      heading.append(title,sub);
      const row = document.createElement("div");
      row.className = "rw-ai-tools-actions";
      row.append(
        makeButton("✦ Solve & explain","solve","calculator.html"),
        makeButton("＋ Similar problems","similar","calculator.html")
      );
      dock.append(heading,row);
      display.insertAdjacentElement("afterend",dock);
    }
    if (page === "homepage.html") {
      const hero = document.querySelector(".hero-section");
      if (hero && !document.getElementById("rwHomeAiGuide")) {
        const button = document.createElement("button");
        button.id = "rwHomeAiGuide";
        button.type = "button";
        button.className = "rw-ecosystem-ai rw-home-ai-guide";
        button.textContent = "✦ Build my path with Rainbow AI";
        button.addEventListener("click", () => window.RainbowBridge.openAI(buildPageContext("general"),"homepage.html"));
        const subtitle = hero.querySelector(".hero-subtitle");
        (subtitle || hero).insertAdjacentElement("afterend",button);
      }
    }
  }
  document.addEventListener("DOMContentLoaded", () => {
    document.body.dataset.rwPage = page.replace(/\.html$/,"");
    document.body.appendChild(bar);
    addActionDock();
  });
  window.RainbowBridge = {
    openAI(prompt, source) {
      const payload = {prompt:String(prompt || "Help me with Rainbow AI.").slice(0,10000),source:String(source || page),createdAt:Date.now()};
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