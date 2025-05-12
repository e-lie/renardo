<script>
  import { onMount } from 'svelte';

  // Available themes - these should match the themes in your tailwind.config.js
  const themes = [
    { name: "Synthwave", value: "synthwave", color: "#e779c1" },
    { name: "Coffee", value: "coffee", color: "#6f4e37" },
    { name: "Pastel", value: "pastel", color: "#bbdefb" },
    { name: "Cyberpunk", value: "cyberpunk", color: "#ff00ff" }
  ];

  // Default theme
  let currentTheme = "cyberpunk";

  onMount(() => {
    // Check for theme in localStorage
    const savedTheme = localStorage.getItem('theme');
    if (savedTheme) {
      currentTheme = savedTheme;
      document.documentElement.setAttribute('data-theme', savedTheme);
    } else {
      // Set default theme if none found
      document.documentElement.setAttribute('data-theme', currentTheme);
      localStorage.setItem('theme', currentTheme);
    }
  });

  // Function to change theme
  function setTheme(theme) {
    document.documentElement.setAttribute('data-theme', theme);
    localStorage.setItem('theme', theme);
    currentTheme = theme;
  }
</script>

<div class="card bg-base-100 shadow-xl mb-8">
  <div class="card-body">
    <h2 class="card-title title-font">
      <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="w-6 h-6 mr-2">
        <path stroke-linecap="round" stroke-linejoin="round" d="M4.098 19.902a3.75 3.75 0 005.304 0l6.401-6.402M6.75 21A3.75 3.75 0 013 17.25V4.125C3 3.504 3.504 3 4.125 3h5.25c.621 0 1.125.504 1.125 1.125v4.072M6.75 21a3.75 3.75 0 003.75-3.75V8.197M6.75 21h13.125c.621 0 1.125-.504 1.125-1.125v-5.25c0-.621-.504-1.125-1.125-1.125h-4.072M10.5 8.197l2.88-2.88c.438-.439 1.15-.439 1.59 0l3.712 3.713c.44.44.44 1.152 0 1.59l-2.879 2.88M6.75 17.25h.008v.008H6.75v-.008z" />
      </svg>
      Theme Selection
    </h2>
    <p class="text-base-content/70 mb-4">Customize your Renardo experience with different visual themes.</p>

    <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
      {#each themes as theme}
        <div
          class="card overflow-hidden cursor-pointer border-4 transition-all {currentTheme === theme.value ? 'border-primary' : 'border-transparent hover:border-base-300'}"
          on:click={() => setTheme(theme.value)}
        >
          <div class="card-body p-4 text-center" data-theme={theme.value} style="min-height: 120px;">
            <h3 class="card-title justify-center mb-2 title-font">{theme.name}</h3>
            <div class="flex justify-center gap-2">
              <span class="badge badge-primary">Primary</span>
              <span class="badge badge-secondary">Secondary</span>
            </div>
            <div class="flex justify-center gap-2 mt-2">
              <span class="badge badge-accent">Accent</span>
              <span class="badge badge-neutral">Neutral</span>
            </div>
          </div>
        </div>
      {/each}
    </div>

    <!-- Theme Descriptions -->
    <div class="mt-8">
      <div class="collapse collapse-arrow bg-base-200">
        <input type="checkbox" />
        <div class="collapse-title text-lg font-medium title-font">
          About the Themes
        </div>
        <div class="collapse-content">
          <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <h4 class="font-bold title-font mb-2">Synthwave</h4>
              <p class="mb-4">A retro-futuristic theme inspired by 80s electronic music and neon aesthetics. Features deep purples with neon pink accents, perfect for nighttime coding sessions.</p>

              <h4 class="font-bold title-font mb-2">Coffee</h4>
              <p class="mb-4">A warm, earthy theme with rich browns and tans reminiscent of your favorite coffee shop. Easy on the eyes for extended coding sessions.</p>
            </div>
            <div>
              <h4 class="font-bold title-font mb-2">Pastel</h4>
              <p class="mb-4">A gentle, soft theme with low-saturation colors that create a calm and soothing environment. Excellent for reducing eye strain.</p>

              <h4 class="font-bold title-font mb-2">Cyberpunk</h4>
              <p class="mb-4">A bold, high-contrast theme with vibrant neon colors on dark backgrounds. Inspired by cyberpunk fiction and perfect for creating futuristic music.</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</div>