// file: src/components/items/children/Item.behavior.test.ts

// import references to testing library "render" and "fireEvent"
import { render, screen, fireEvent } from '@testing-library/svelte'

// import reference to our interface
import type { ItemInterface } from '@/models'
// import reference to your Item component:
import ItemComponent from './Item.component.svelte'

describe('Item.component: behavior', () => {
  // Note: This is as an async test as we are using `fireEvent`
  it('click event invokes onItemSelect handler as expected', async () => {
    // our data to pass to our component:
    const item: ItemInterface = {
      id: 1,
      name: 'Unit test item 1',
      selected: false
    }

    const testid = 'unit-test-behavior-1'

    // using testing library "render" to get the element by text
    const { component } = render(ItemComponent, {
      testid,
      item
    })

    // get element reference by testid
    const liElement = screen.getByTestId(testid)

    // create a spy function with vitest.fn()
    const mockOnItemSelect = vitest.fn()
    // wire up the spy function on the event that is dispatched as 'selectEvent"
    component.$on('selectItem', mockOnItemSelect)
    // trigger click on the <li> element:
    // Note: In svelte testing library we have to use await when firing events
    // because we must wait for the next `tick` to allow for Svelte to flush all pending state changes.
    await fireEvent.click(liElement)

    // check test result (should have been called once)
    expect(mockOnItemSelect).toHaveBeenCalledTimes(1)
  })
})
