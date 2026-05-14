const lessons = [
  {
    id: "freedom",
    index: 1,
    title: "สร้างพอร์ต 300 เท่า Way to Financial Freedom",
    category: "Mindset",
    minutes: 211,
    url: "https://www.youtube.com/watch?v=bQVVbXxh6Pg",
    focus: "ภาพใหญ่ของอิสรภาพทางการเงินและเหตุผลที่ technical เป็นแค่ส่วนหนึ่งของเกม",
    takeaway: "เริ่มจากเป้าหมาย ระบบคิด และความเข้าใจ risk/reward ก่อนลงรายละเอียดเครื่องมือ"
  },
  {
    id: "beer",
    index: 2,
    title: "เคล็ดลับการเทรดในแบบ เบียร์ วนนท์",
    category: "Trader Mind",
    minutes: 177,
    url: "https://www.youtube.com/watch?v=rSMMdrdPcBk",
    focus: "วิธีคิด ประสบการณ์ และ pattern การตัดสินใจของนักเทรด",
    takeaway: "ดึงหลักคิดจาก trader case study แล้วแปลงเป็น checklist ของตัวเอง"
  },
  {
    id: "safe-growth",
    index: 3,
    title: "สูตรปั้นพอร์ตอย่างปลอดภัย",
    category: "Risk",
    minutes: 189,
    url: "https://www.youtube.com/watch?v=8QJMisxXiOA",
    focus: "การโตของพอร์ตโดยไม่ทำลายทุน",
    takeaway: "ผลตอบแทนที่ดีต้องมาพร้อมขอบเขตความเสี่ยงและจังหวะการเพิ่มน้ำหนัก"
  },
  {
    id: "set100",
    index: 4,
    title: "เทรดหุ้น SET100 ยังไงให้ได้หลักล้าน",
    category: "Strategy",
    minutes: 168,
    url: "https://www.youtube.com/watch?v=m15Qty91TB4",
    focus: "การเลือกสนามเทรดในหุ้นขนาดใหญ่",
    takeaway: "หุ้นใหญ่มีสภาพคล่องและพฤติกรรมต่างจากหุ้นเล็ก ต้องอ่านเกมให้เหมาะกับสนาม"
  },
  {
    id: "prop",
    index: 5,
    title: "Prop Trade Professional",
    category: "Execution",
    minutes: 178,
    url: "https://www.youtube.com/watch?v=itpnZ-ypF9w",
    focus: "วินัย การจัดการสถานะ และวิธีคิดแบบมืออาชีพ",
    takeaway: "คิดเป็น process ไม่ใช่คิดเป็นไม้เดียว"
  },
  {
    id: "swing",
    index: 6,
    title: "Swing Trade Professional Trader",
    category: "Strategy",
    minutes: 180,
    url: "https://www.youtube.com/watch?v=SuK4SiRGZFs",
    focus: "การจับรอบหลายวันถึงหลายสัปดาห์",
    takeaway: "Swing trade ต้องผสม trend, timing, risk และ patience"
  },
  {
    id: "money-game",
    index: 7,
    title: "Money Game บ้านหนึ่งหลัง รถสองคัน",
    category: "Mindset",
    minutes: 157,
    url: "https://www.youtube.com/watch?v=8jXMm46UCH4",
    focus: "เป้าหมายชีวิตกับเป้าหมายการลงทุน",
    takeaway: "เป้าหมายทางการเงินต้องแปลงเป็นระบบการลงมือที่วัดผลได้"
  },
  {
    id: "scalper",
    index: 8,
    title: "Scalper เทรดสั้น ปั้นพอร์ต",
    category: "Execution",
    minutes: 166,
    url: "https://www.youtube.com/watch?v=1ymZXCfr3YQ",
    focus: "การเทรดสั้นและการอ่านแรงซื้อขายระยะใกล้",
    takeaway: "Scalping ต้องเร็ว ชัด และยอมผิดทันทีเมื่อ market ไม่ให้"
  },
  {
    id: "all-in",
    index: 9,
    title: "วิธีการ All in ด้วย Fundamental",
    category: "Fundamental",
    minutes: 166,
    url: "https://www.youtube.com/watch?v=7g8iXgPsmfs",
    focus: "การใช้พื้นฐานเพื่อเพิ่ม conviction",
    takeaway: "All in ไม่ใช่ความกล้าอย่างเดียว แต่ต้องมี thesis, catalyst และแผนรับมือ"
  },
  {
    id: "daytrade",
    index: 10,
    title: "อ่านใจเจ้ามือแบบ Day Trade",
    category: "Execution",
    minutes: 159,
    url: "https://www.youtube.com/watch?v=BxzHjabFKYs",
    focus: "พฤติกรรมราคาในวันและร่องรอยของแรง",
    takeaway: "อ่านเจ้ามือคืออ่าน supply, demand, trap และ reaction ไม่ใช่เดาใจคน"
  },
  {
    id: "trading-strategy",
    index: 11,
    title: "Trading Strategy",
    category: "Strategy",
    minutes: 186,
    url: "https://www.youtube.com/watch?v=dIpBqYfLYN0",
    focus: "การประกอบระบบเทรดจากหลายองค์ประกอบ",
    takeaway: "กลยุทธ์ที่ดีต้องตอบว่าเข้าเมื่อไร ออกเมื่อไร ผิดตรงไหน และวัดผลอย่างไร"
  },
  {
    id: "elliott",
    index: 12,
    title: "Elliott Wave + Fibonacci",
    category: "Technical",
    minutes: 147,
    url: "https://www.youtube.com/watch?v=cQ_YxsAan6M",
    focus: "โครงสร้างคลื่นและจุดวัดสัดส่วนราคา",
    takeaway: "ใช้ wave/fibo เป็นแผนที่ความน่าจะเป็น ไม่ใช่คำทำนายตายตัว"
  },
  {
    id: "bid-offer",
    index: 13,
    title: "Bid Offer Analysis",
    category: "Order Flow",
    minutes: 148,
    url: "https://www.youtube.com/watch?v=51r_jnv28NU",
    focus: "การอ่านช่อง Bid/Offer และแรงที่ซ่อนในกระดาน",
    takeaway: "กระดานช่วยเห็นเจตนาใกล้ ๆ แต่ต้องยืนยันด้วยราคาและ volume"
  },
  {
    id: "wyckoff",
    index: 14,
    title: "Volume Analysis + Wyckoff",
    category: "Volume",
    minutes: 175,
    url: "https://www.youtube.com/watch?v=tKfPCwGwb7w",
    focus: "แรงสะสม แจกจ่าย และ phase ของราคา",
    takeaway: "Wyckoff ทำให้เห็น story ระหว่างราคา volume และพฤติกรรมผู้เล่นใหญ่"
  },
  {
    id: "volume",
    index: 15,
    title: "Volume Analysis",
    category: "Volume",
    minutes: 160,
    url: "https://www.youtube.com/watch?v=gABlsxvPVas",
    focus: "การตีความ volume เทียบกับ price action",
    takeaway: "Volume คือหลักฐานของความจริงจัง ต้องอ่านคู่กับตำแหน่งราคา"
  },
  {
    id: "financials",
    index: 16,
    title: "ศิลปะการแกะงบหาหุ้น",
    category: "Fundamental",
    minutes: 161,
    url: "https://www.youtube.com/watch?v=AGFOnephQ6k",
    focus: "การอ่านงบเพื่อหาคุณภาพและ story ของกิจการ",
    takeaway: "งบการเงินช่วยแยกหุ้นมี story จริงออกจากหุ้นที่มีแค่ราคาเคลื่อนไหว"
  },
  {
    id: "basic-tech-2",
    index: 17,
    title: "Basic Technical 2",
    category: "Technical",
    minutes: 128,
    url: "https://www.youtube.com/watch?v=hpB9XzDhYIU",
    focus: "พื้นฐาน technical สำหรับต่อยอด",
    takeaway: "เครื่องมือ technical ต้องถูกใช้เพื่ออ่าน context ไม่ใช่สะสม indicator"
  },
  {
    id: "basic-tech-1",
    index: 18,
    title: "Basic Technical 1",
    category: "Technical",
    minutes: 130,
    url: "https://www.youtube.com/watch?v=0EWjzXoDexE",
    focus: "ภาษาเบื้องต้นของกราฟ ราคา และแนวโน้ม",
    takeaway: "เข้าใจ price structure ก่อนค่อยเพิ่มเครื่องมืออื่น"
  },
  {
    id: "strategist",
    index: 19,
    title: "การวิเคราะห์หุ้นในแบบฉบับนักกลยุทธ์",
    category: "Strategy",
    minutes: 152,
    url: "https://www.youtube.com/watch?v=StvPf-ASoW4",
    focus: "การมองหุ้นแบบวางแผนหลายมิติ",
    takeaway: "นักกลยุทธ์ไม่ถามแค่ว่าขึ้นไหม แต่ถามว่า scenario ไหนคุ้มที่สุด"
  },
  {
    id: "account",
    index: 20,
    title: "การเปิดบัญชีซื้อขายหลักทรัพย์ Streaming EFin",
    category: "Tools",
    minutes: 71,
    url: "https://www.youtube.com/watch?v=p3ehk9gWyCs",
    focus: "เครื่องมือเริ่มต้นสำหรับลงมือจริง",
    takeaway: "เครื่องมือควรถูกจัดให้พร้อม เพื่อให้การฝึกไม่สะดุดตอนต้องลงมือ"
  }
];

const topics = [
  {
    name: "Mindset",
    label: "เป้าหมายและกรอบคิด",
    angle: 260,
    lessons: ["freedom", "money-game", "beer"],
    prompt: "ตอบให้ได้ว่าเรียนหุ้นไปเพื่ออะไร รับ drawdown ได้แค่ไหน และจะวัดความคืบหน้าอย่างไร"
  },
  {
    name: "Technical",
    label: "ภาษาอ่านกราฟ",
    angle: 318,
    lessons: ["basic-tech-1", "basic-tech-2", "elliott"],
    prompt: "อ่าน trend, structure, key level แล้วแปลงเป็นจุดเข้าออกที่ตรวจสอบได้"
  },
  {
    name: "Volume",
    label: "แรงซื้อขาย",
    angle: 20,
    lessons: ["volume", "wyckoff", "bid-offer"],
    prompt: "ดูว่าราคาขยับด้วยแรงจริงหรือแรงหลอก โดยเทียบ price, volume และ order flow"
  },
  {
    name: "Fundamental",
    label: "คุณภาพกิจการ",
    angle: 82,
    lessons: ["financials", "all-in"],
    prompt: "สร้าง thesis จากงบและ story แล้วรู้ว่าข้อมูลไหนทำให้ thesis พัง"
  },
  {
    name: "Strategy",
    label: "ระบบเทรด",
    angle: 145,
    lessons: ["safe-growth", "set100", "swing", "trading-strategy", "strategist"],
    prompt: "ประกอบ entry, exit, sizing, invalidation และ review loop ให้เป็นระบบเดียว"
  },
  {
    name: "Execution",
    label: "การลงมือจริง",
    angle: 205,
    lessons: ["prop", "scalper", "daytrade", "account"],
    prompt: "ฝึกจังหวะ การตัดสินใจ ความเร็ว และวินัยในสภาพตลาดจริง"
  }
];

const cards = [
  {
    q: "ทำไม Technical Analysis อย่างเดียวไม่พอ?",
    a: "เพราะกราฟเป็นเพียงเครื่องมืออ่านพฤติกรรมราคา แต่ผลลัพธ์จริงยังขึ้นกับ mindset, risk, sizing, strategy และ execution"
  },
  {
    q: "เวลาเรียนบท Volume หรือ Wyckoff ต้องถามอะไรเสมอ?",
    a: "แรงที่เห็นเป็นแรงจริงหรือแรงหลอก อยู่ในตำแหน่งราคาแบบไหน และตลาดตอบสนองต่อ volume นั้นอย่างไร"
  },
  {
    q: "สูตรปั้นพอร์ตอย่างปลอดภัยควรเริ่มจากอะไร?",
    a: "เริ่มจากการนิยามความเสี่ยงสูงสุดต่อไม้ ต่อวัน ต่อรอบ และรู้ว่าจุดไหนต้องหยุดก่อนคิดเรื่องกำไร"
  },
  {
    q: "Bid/Offer ใช้ดีที่สุดเมื่อจับคู่กับอะไร?",
    a: "จับคู่กับ price action, volume และ reaction หลังแตะระดับสำคัญ เพราะกระดานอย่างเดียวถูกหลอกได้"
  },
  {
    q: "Mind map ของ The Legend ควรจำแกนหลักกี่ด้าน?",
    a: "6 ด้าน: Mindset, Technical, Volume, Fundamental, Strategy และ Execution"
  }
];

const quiz = [
  {
    q: "บทไหนเหมาะที่สุดสำหรับเริ่มจากภาพใหญ่ก่อนลงเครื่องมือ?",
    options: ["สร้างพอร์ต 300 เท่า", "Bid Offer Analysis", "การเปิดบัญชี", "Basic Technical 2"],
    answer: 0
  },
  {
    q: "ถ้าอยากอ่านแรงสะสมและแจกจ่าย ควรไปที่แกนไหน?",
    options: ["Tools", "Volume/Wyckoff", "Mindset", "Account Setup"],
    answer: 1
  },
  {
    q: "คำถามสำคัญของ strategy ที่ดีคืออะไร?",
    options: ["ใช้ indicator กี่ตัว", "เข้า ออก ผิดตรงไหน และวัดผลอย่างไร", "คลิปไหนยาวที่สุด", "หุ้นจะขึ้นแน่นอนไหม"],
    answer: 1
  },
  {
    q: "Fundamental ช่วยเรื่องใดมากที่สุด?",
    options: ["เพิ่มความเร็วในการคลิก", "หา thesis และคุณภาพกิจการ", "ทำให้ไม่ต้อง stop loss", "แทน volume ได้ทั้งหมด"],
    answer: 1
  }
];

const state = {
  done: new Set(JSON.parse(localStorage.getItem("legend.done") || "[]")),
  note: localStorage.getItem("legend.note") || "",
  cardIndex: 0,
  quizIndex: 0,
  selectedTopic: topics[0].name
};

const views = {
  dashboard: document.querySelector("#dashboardView"),
  coach: document.querySelector("#coachView"),
  roadmap: document.querySelector("#roadmapView"),
  mindmap: document.querySelector("#mindmapView"),
  review: document.querySelector("#reviewView"),
  quiz: document.querySelector("#quizView")
};

const viewTitles = {
  dashboard: "ภาพรวมการเรียน",
  coach: "Coach Mode ส่วนตัว",
  roadmap: "Roadmap ทั้ง 20 บท",
  mindmap: "Mind Map แกนความรู้",
  review: "ทบทวนให้เข้าหัว",
  quiz: "Quiz ตรวจความเข้าใจ"
};

function saveDone() {
  localStorage.setItem("legend.done", JSON.stringify([...state.done]));
}

function lessonById(id) {
  return lessons.find((lesson) => lesson.id === id);
}

function formatTime(minutes) {
  const h = Math.floor(minutes / 60);
  const m = minutes % 60;
  return h ? `${h} ชม. ${m} นาที` : `${m} นาที`;
}

function updateProgress() {
  const doneCount = state.done.size;
  const percent = Math.round((doneCount / lessons.length) * 100);
  document.querySelector("#overallPercent").textContent = `${percent}%`;
  document.querySelector("#overallBar").style.width = `${percent}%`;
  document.querySelector("#doneLessons").textContent = doneCount;
  const next = lessons.find((lesson) => !state.done.has(lesson.id));
  document.querySelector("#nextSuggestion").textContent = next
    ? `บทถัดไปที่ยังไม่จบ: ${next.title}`
    : "ครบทุกบทแล้ว รอบต่อไปให้เน้น quiz และจด thesis จากกราฟจริง";
  renderNextLesson();
}

function renderLearningPath() {
  const path = [
    "ภาพใหญ่และเป้าหมาย: Mindset, Money Game, Trader Mind",
    "พื้นฐานการอ่านกราฟ: Basic Technical, Elliott Wave, Fibonacci",
    "แรงและพฤติกรรมผู้เล่น: Volume, Wyckoff, Bid/Offer",
    "คุณภาพหุ้น: แกะงบ, Fundamental conviction",
    "ระบบเทรด: Swing, SET100, Trading Strategy, Strategist",
    "Execution: Scalper, Day Trade, Prop Trade, เครื่องมือจริง"
  ];
  document.querySelector("#learningPath").innerHTML = path.map((item) => `<li>${item}</li>`).join("");
}

function renderNextLesson() {
  const next = lessons.find((lesson) => !state.done.has(lesson.id)) || lessons[0];
  document.querySelector("#nextLessonCard").innerHTML = lessonCardInner(next, true);
}

function lessonCardInner(lesson, compact = false) {
  const done = state.done.has(lesson.id);
  return `
    <div class="lesson-topline">
      <span class="tag">${lesson.category}</span>
      <span class="lesson-meta">บท ${lesson.index} · ${formatTime(lesson.minutes)}</span>
    </div>
    <h3>${lesson.title}</h3>
    <p>${lesson.focus}</p>
    ${compact ? `<p><strong>จำให้ได้:</strong> ${lesson.takeaway}</p>` : ""}
    <div class="lesson-actions">
      <a class="ghost-btn" href="${lesson.url}" target="_blank" rel="noreferrer">เปิดวิดีโอ</a>
      <button class="status-btn ${done ? "done" : ""}" data-toggle="${lesson.id}">
        ${done ? "เรียนจบแล้ว" : "ติ๊กว่าจบ"}
      </button>
    </div>
  `;
}

function renderLessons(filter = "") {
  const normalized = filter.trim().toLowerCase();
  const visible = lessons.filter((lesson) => {
    const haystack = `${lesson.title} ${lesson.category} ${lesson.focus} ${lesson.takeaway}`.toLowerCase();
    return haystack.includes(normalized);
  });
  document.querySelector("#lessonGrid").innerHTML = visible
    .map((lesson) => `<article class="lesson-card">${lessonCardInner(lesson)}</article>`)
    .join("");
}

function renderMindmap() {
  const nodes = topics.map((topic) => {
    const rad = (topic.angle * Math.PI) / 180;
    const x = 50 + Math.cos(rad) * 34;
    const y = 50 + Math.sin(rad) * 34;
    const lessonCount = topic.lessons.length;
    return `
      <button class="mind-node" style="left: calc(${x}% - 105px); top: calc(${y}% - 43px);" data-topic="${topic.name}">
        <strong>${topic.label}</strong>
        <span class="node-lessons">${lessonCount} บทเรียน · ${topic.name}</span>
      </button>
    `;
  });
  document.querySelector("#mindmapNodes").innerHTML = nodes.join("");
  renderTopicDetail(state.selectedTopic);
}

function renderTopicDetail(topicName) {
  const topic = topics.find((item) => item.name === topicName) || topics[0];
  const topicLessons = topic.lessons.map(lessonById);
  document.querySelector("#topicDetail").innerHTML = `
    <div class="panel-heading">
      <h3>${topic.label}</h3>
      <span>${topic.name}</span>
    </div>
    <p>${topic.prompt}</p>
    <div class="lesson-grid">
      ${topicLessons.map((lesson) => `
        <article class="lesson-card">
          <div class="lesson-topline">
            <span class="tag">บท ${lesson.index}</span>
            <span class="lesson-meta">${formatTime(lesson.minutes)}</span>
          </div>
          <h3>${lesson.title}</h3>
          <p>${lesson.takeaway}</p>
        </article>
      `).join("")}
    </div>
  `;
}

function renderFlashcard(showAnswer = false) {
  const card = cards[state.cardIndex];
  document.querySelector("#cardQuestion").textContent = card.q;
  document.querySelector("#cardAnswer").textContent = showAnswer ? card.a : "กดเฉลยเมื่อพร้อม";
}

function renderQuiz() {
  const item = quiz[state.quizIndex];
  document.querySelector("#quizQuestion").textContent = item.q;
  document.querySelector("#quizCounter").textContent = `ข้อ ${state.quizIndex + 1}/${quiz.length}`;
  document.querySelector("#quizFeedback").textContent = "";
  document.querySelector("#quizOptions").innerHTML = item.options
    .map((option, index) => `<button class="quiz-option" data-answer="${index}">${option}</button>`)
    .join("");
}

function renderCoachModule() {
  if (typeof courseModules === "undefined" || !courseModules.length) return;
  const module = courseModules[0];
  document.querySelector("#moduleTitle").textContent = module.title;
  document.querySelector("#moduleMission").textContent = module.mission;
  document.querySelector("#moduleCore").innerHTML = module.core.map((item) => `<li>${item}</li>`).join("");
  document.querySelector("#moduleFramework").innerHTML = module.framework.map((item) => `<li>${item}</li>`).join("");
  document.querySelector("#scenarioPrompt").textContent = module.scenario.prompt;
  document.querySelector("#scenarioOptions").innerHTML = module.scenario.options
    .map((option, index) => `<button class="quiz-option" data-scenario-answer="${index}">${option}</button>`)
    .join("");
  document.querySelector("#moduleExercises").innerHTML = module.exercises
    .map((exercise, index) => `
      <div class="exercise-item">
        <label for="exercise-${index}">${index + 1}. ${exercise}</label>
        <textarea id="exercise-${index}" data-module-note="${index}" placeholder="เขียนตอบด้วยภาษาของตัวเอง"></textarea>
      </div>
    `)
    .join("");
  document.querySelector("#moduleMastery").innerHTML = module.mastery
    .map((item, index) => `
      <div class="mastery-item">
        <label for="mastery-${index}">${item}: <span id="mastery-value-${index}">0</span>/5</label>
        <input id="mastery-${index}" type="range" min="0" max="5" value="0" data-mastery="${index}">
      </div>
    `)
    .join("");

  const savedNotes = JSON.parse(localStorage.getItem("legend.module01.notes") || "{}");
  document.querySelectorAll("[data-module-note]").forEach((field) => {
    field.value = savedNotes[field.dataset.moduleNote] || "";
  });
  const savedMastery = JSON.parse(localStorage.getItem("legend.module01.mastery") || "{}");
  document.querySelectorAll("[data-mastery]").forEach((slider) => {
    slider.value = savedMastery[slider.dataset.mastery] || 0;
    document.querySelector(`#mastery-value-${slider.dataset.mastery}`).textContent = slider.value;
  });
  updateModuleScore();
}

function updateModuleScore() {
  const total = [...document.querySelectorAll("[data-mastery]")]
    .reduce((sum, slider) => sum + Number(slider.value), 0);
  document.querySelector("#moduleScore").textContent = `${total}/20`;
}

function switchView(viewName) {
  Object.entries(views).forEach(([name, element]) => {
    element.classList.toggle("active", name === viewName);
  });
  document.querySelectorAll(".nav-tab").forEach((button) => {
    button.classList.toggle("active", button.dataset.view === viewName);
  });
  document.querySelector("#viewTitle").textContent = viewTitles[viewName];
}

document.addEventListener("click", (event) => {
  const nav = event.target.closest("[data-view]");
  if (nav) switchView(nav.dataset.view);

  const toggle = event.target.closest("[data-toggle]");
  if (toggle) {
    const id = toggle.dataset.toggle;
    if (state.done.has(id)) state.done.delete(id);
    else state.done.add(id);
    saveDone();
    renderLessons(document.querySelector("#searchInput").value);
    updateProgress();
  }

  const topic = event.target.closest("[data-topic]");
  if (topic) {
    state.selectedTopic = topic.dataset.topic;
    renderTopicDetail(state.selectedTopic);
  }

  const answer = event.target.closest("[data-answer]");
  if (answer) {
    const selected = Number(answer.dataset.answer);
    const item = quiz[state.quizIndex];
    document.querySelectorAll(".quiz-option").forEach((button) => {
      const isCorrect = Number(button.dataset.answer) === item.answer;
      const isSelected = Number(button.dataset.answer) === selected;
      button.classList.toggle("correct", isCorrect);
      button.classList.toggle("wrong", isSelected && !isCorrect);
    });
    document.querySelector("#quizFeedback").textContent = selected === item.answer
      ? "ถูกต้อง เก็บแกนคิดนี้ไว้ใช้กับกราฟจริง"
      : "ยังไม่ใช่ ลองดูคำตอบที่ไฮไลต์แล้วกลับไปโยงกับ mind map";
  }

  const scenarioAnswer = event.target.closest("[data-scenario-answer]");
  if (scenarioAnswer && typeof courseModules !== "undefined") {
    const selected = Number(scenarioAnswer.dataset.scenarioAnswer);
    const scenario = courseModules[0].scenario;
    document.querySelectorAll("[data-scenario-answer]").forEach((button) => {
      const isCorrect = Number(button.dataset.scenarioAnswer) === scenario.answer;
      const isSelected = Number(button.dataset.scenarioAnswer) === selected;
      button.classList.toggle("correct", isCorrect);
      button.classList.toggle("wrong", isSelected && !isCorrect);
    });
    document.querySelector("#scenarioFeedback").textContent = selected === scenario.answer
      ? scenario.feedback
      : "ยังไม่ผ่าน จุดนี้คือกับดัก FOMO ให้กลับไปถามว่า หลักฐานคืออะไร และถ้าผิดจะเสียเท่าไร";
  }
});

document.querySelector("#searchInput").addEventListener("input", (event) => {
  renderLessons(event.target.value);
});

document.querySelector("#showAnswerBtn").addEventListener("click", () => renderFlashcard(true));
document.querySelector("#nextCardBtn").addEventListener("click", () => {
  state.cardIndex = (state.cardIndex + 1) % cards.length;
  renderFlashcard(false);
});

document.querySelector("#saveNoteBtn").addEventListener("click", () => {
  const note = document.querySelector("#studyNote").value;
  localStorage.setItem("legend.note", note);
  document.querySelector("#saveNoteBtn").textContent = "บันทึกแล้ว";
  window.setTimeout(() => {
    document.querySelector("#saveNoteBtn").textContent = "บันทึกโน้ต";
  }, 1200);
});

document.querySelector("#nextQuizBtn").addEventListener("click", () => {
  state.quizIndex = (state.quizIndex + 1) % quiz.length;
  renderQuiz();
});

document.querySelector("#saveModuleBtn").addEventListener("click", () => {
  const notes = {};
  document.querySelectorAll("[data-module-note]").forEach((field) => {
    notes[field.dataset.moduleNote] = field.value;
  });
  localStorage.setItem("legend.module01.notes", JSON.stringify(notes));
  document.querySelector("#saveModuleBtn").textContent = "บันทึกแล้ว";
  window.setTimeout(() => {
    document.querySelector("#saveModuleBtn").textContent = "บันทึกคำตอบ";
  }, 1200);
});

document.addEventListener("input", (event) => {
  const mastery = event.target.closest("[data-mastery]");
  if (!mastery) return;
  document.querySelector(`#mastery-value-${mastery.dataset.mastery}`).textContent = mastery.value;
  const values = {};
  document.querySelectorAll("[data-mastery]").forEach((slider) => {
    values[slider.dataset.mastery] = slider.value;
  });
  localStorage.setItem("legend.module01.mastery", JSON.stringify(values));
  updateModuleScore();
});

document.querySelector("#studyNote").value = state.note;
document.querySelector("#totalLessons").textContent = lessons.length;
renderLearningPath();
renderLessons();
renderMindmap();
renderFlashcard(false);
renderQuiz();
renderCoachModule();
updateProgress();
