const CompilerType = {
  PYTHON: 'python',
};

class Compiler {
  constructor(compilerId) {
    this.compilerId = compilerId;
    this.urlExecute = `https://api-compiler.onrender.com/api/${CompilerType.PYTHON}/run`;
    this.baseUrl = 'https://api-compiler.onrender.com';
    this.WSbaseUrl = 'ws://api-compiler.onrender.com:8000';

    this.socket_config = {
      path: '/ws/socket.io',
      transports: ['websocket', 'polling', 'flashsocket'],
    };
    this.socket = io(this.WSbaseUrl, this.socket_config);
    this.uuid = '';
    this.editorInput = null;
    this.outputRef = null;
    this.HandleInputRef = null;
  }

  handleInputKeyDown(event) {
    if (event.key === 'Enter') {
      event.preventDefault();
      this.sendInput();
    }
  }

  sendInput() {
    this.socket.emit('prompt', this.uuid, this.HandleInputRef.value);
    this.outputRef.value += this.HandleInputRef.value + "\n";
    this.HandleInputRef.value = "";
  }

  async executeCode(code) {
    this.outputRef.value = "";
    const rsp = await fetch(this.urlExecute, {
      mode: 'cors',
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ code }),
    });
    const data = await rsp.json();

    if (data.uuid) {
      this.uuid = data.uuid;
      this.socket.emit('processconnect', this.uuid);
    } else {
      return `${data.output}\n${data.error}`;
    }
  }

  handleResponse(data, data_uuid) {
    if (this.uuid === data_uuid) {
      this.outputRef.value += data;
    }
  }

  handleProcessEnd(data_uuid) {
    if (data_uuid === this.uuid) {
      this.outputRef.value += '\nПроцесс завершен';
    }
  }

  initialize() {
    this.editorInput = CodeMirror.fromTextArea(document.querySelector(`#Input${this.compilerId}`), {
      mode: 'python',
      theme: 'default',
      lineNumbers: true,
      tabSize: 4,
    });
    this.outputRef = document.querySelector(`#Output${this.compilerId}`);
    this.HandleInputRef = document.querySelector(`#HandleInput${this.compilerId}`);
    this.HandleInputRef.addEventListener('keydown', this.handleInputKeyDown.bind(this));

    document.querySelector(`#HandleInputGO${this.compilerId}`).addEventListener('click', this.sendInput.bind(this));
    document.querySelector(`#consoleGo${this.compilerId}`).addEventListener('click', this.consoleGo.bind(this));
    document.querySelector(`#saveCodeToFile${this.compilerId}`).addEventListener('click', this.saveCodeToFile.bind(this));

    this.socket.on('response', this.handleResponse.bind(this));
    this.socket.on('processend', this.handleProcessEnd.bind(this));

    window.addEventListener('beforeunload', () => {
      this.socket.off('response');
      this.socket.off('processend');
    });
  }

  saveCodeToFile() {
    const userInput = this.editorInput.getValue();
    const blob = new Blob([userInput], { type: 'text/plain;charset=utf-8' });
    const link = document.createElement('a');
    link.href = URL.createObjectURL(blob);
    link.download = 'code.py';
    link.click();
  }

  async consoleGo() {
    const inputText = this.editorInput.getValue();
    const outputText = await this.executeCode(inputText);
    if (outputText != null) {
      this.outputRef.value = outputText;
    }
  }
}

class CompilerFactory {
  createCompiler(compilerId) {
    const compiler = new Compiler(compilerId);
    compiler.initialize();
    return compiler;
  }
}

document.addEventListener('DOMContentLoaded', () => {
  const compilerFactory = new CompilerFactory();

  const compilers = ['1', '2', '3'];

  compilers.forEach((compilerId) => {
    compilerFactory.createCompiler(compilerId);
  });
});
