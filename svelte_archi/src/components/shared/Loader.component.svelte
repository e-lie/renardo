<div class="loader">
  <div class="bounceball" />
</div>

<style>
  .loader {
    display: inline-block;
  }
  .loader .bounceball {
    position: relative;
    width: 30px;
  }
  .loader .bounceball:before {
    position: absolute;
    content: '';
    top: 0;
    width: 30px;
    height: 30px;
    border-radius: 50%;
    background-color: #ff3e00;
    transform-origin: 50%;
    animation: bounce 500ms alternate infinite ease;
  }
  @keyframes bounce {
    0% {
      top: 60px;
      height: 10px;
      border-radius: 60px 60px 20px 20px;
      transform: scaleX(2);
    }
    25% {
      height: 60px;
      border-radius: 50%;
      transform: scaleX(1);
    }
    100% {
      top: 0;
    }
  }
</style>
