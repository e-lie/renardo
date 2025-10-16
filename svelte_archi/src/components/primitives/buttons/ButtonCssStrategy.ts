const buttonCssStrategy = new Map<string, string>()

buttonCssStrategy.set('primary', 'bg-blue-500 text-white hover:bg-blue-400 focus:ring-blue-300')
buttonCssStrategy.set('secondary', 'bg-white text-gray-700 border-gray-300 hover:border-gray-700 focus:ring-gray-300')
buttonCssStrategy.set('danger', 'bg-red-500 text-white hover:bg-red-700 focus:ring-red-500')

export { buttonCssStrategy }
