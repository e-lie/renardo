<script>
  import { onMount } from 'svelte';

  // Available themes - these should match the themes in your tailwind.config.js
  const themes = [
    { name: "Default", value: "default", icon: "🦄" },
    { name: "Synthwave", value: "synthwave", icon: "🎸" },
    { name: "Coffee", value: "coffee", icon: "☕" },
    { name: "Pastel", value: "pastel", icon: "🎨" },
    { name: "Cyberpunk", value: "cyberpunk", icon: "🤖" }
  ];

  // Current theme
  let currentTheme = "default";
  let dropdownOpen = false;

  onMount(() => {
    // Check for theme in localStorage
    const savedTheme = localStorage.getItem('theme');
    if (savedTheme) {
      currentTheme = savedTheme;
    }
  });

  // Function to change theme
  function setTheme(theme) {
    document.documentElement.setAttribute('data-theme', theme);
    localStorage.setItem('theme', theme);
    currentTheme = theme;
    dropdownOpen = false;
  }

  // Toggle dropdown
  function toggleDropdown() {
    dropdownOpen = !dropdownOpen;
  }

  // Close dropdown when clicking outside
  function handleClickOutside(event) {
    if (dropdownOpen && !event.target.closest('.theme-dropdown')) {
      dropdownOpen = false;
    }
  }
</script>

<svelte:window on:click={handleClickOutside} />

<div class="theme-dropdown dropdown dropdown-end">
  <button class="btn btn-ghost btn-circle" on:click={toggleDropdown}>
    <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="w-6 h-6">
      <path stroke-linecap="round" stroke-linejoin="round" d="M4.098 19.902a3.75 3.75 0 005.304 0l6.401-6.402M6.75 21A3.75 3.75 0 013 17.25V4.125C3 3.504 3.504 3 4.125 3h5.25c.621 0 1.125.504 1.125 1.125v4.072M6.75 21a3.75 3.75 0 003.75-3.75V8.197M6.75 21h13.125c.621 0 1.125-.504 1.125-1.125v-5.25c0-.621-.504-1.125-1.125-1.125h-4.072M10.5 8.197l2.88-2.88c.438-.439 1.15-.439 1.59 0l3.712 3.713c.44.44.44 1.152 0 1.59l-2.879 2.88M6.75 17.25h.008v.008H6.75v-.008z" />
    </svg>
  </button>
  {#if dropdownOpen}
    <div class="dropdown-content z-[1] menu p-2 shadow bg-base-200 rounded-box w-52 absolute right-0 mt-2">
      <div class="menu-title text-center title-font">Change Theme</div>
      {#each themes as theme}
        <button
          class="w-full text-left p-2 hover:bg-base-300 rounded cursor-pointer {currentTheme === theme.value ? 'bg-base-300' : ''}"
          on:click={() => setTheme(theme.value)}
          on:keydown={(e) => e.key === 'Enter' && setTheme(theme.value)}
        >
          <div class="flex items-center gap-2">
            <span>{theme.icon}</span>
            <span class="title-font">{theme.name}</span>
            {#if currentTheme === theme.value}
              <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="w-4 h-4 ml-auto">
                <path stroke-linecap="round" stroke-linejoin="round" d="M4.5 12.75l6 6 9-13.5" />
              </svg>
            {/if}
          </div>
        </button>
      {/each}
    </div>
  {/if}
</div>