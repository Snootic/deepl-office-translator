const { invoke } = window.__TAURI__.tauri;
const { open } = window.__TAURI__.dialog
const { appDir } = window.__TAURI__.path;
import { initializeKeys, apiKey, keys } from "./getApiKeys.js";
import {message} from "./message.js";

await initializeKeys()

const divConfirmar = document.querySelector("#confirm-submit");
const formTraduzir = document.getElementById("file-form");

const targetFileInput = document.getElementById("target-file-input")

const confirmarGlossario = document.getElementById("glossary_confirm");
const confirmarTargLang = document.getElementById("target_language_confirm");
const confirmarSrcLang = document.getElementById("source_language_confirm");
const confirmarArquivoOriginal = document.getElementById("original_file_confirm");
const confirmarArquivoDestino = document.getElementById("target_file_confirm");
const confirmarTraducaoBotao = document.getElementById("confirm-translation");
const cancelarTraducaoBotao = document.getElementById("cancel-translation");

formTraduzir.addEventListener("submit", async (event) => {
    event.preventDefault();
    divConfirmar.classList.add("show");

    let formData = new FormData(formTraduzir);

    // Exibindo os valores na interface de confirmação
    confirmarSrcLang.value = document.getElementById("source-language").options[document.getElementById("source-language").selectedIndex].innerHTML;
    confirmarTargLang.value = document.getElementById("target-language").options[document.getElementById("target-language").selectedIndex].innerHTML;
    confirmarGlossario.value = document.getElementById("glossary-select").options[document.getElementById("glossary-select").selectedIndex].innerHTML;
    
    const originalFile = formData.get("original-file-input");
    confirmarArquivoOriginal.value = originalFile ? originalFile.name : "Nenhum arquivo selecionado";
    
    confirmarArquivoDestino.value = formData.get("target-file-input");
});

confirmarTraducaoBotao.addEventListener("click", async (event) => {
    event.preventDefault();
    const formData = new FormData(formTraduzir);

    const originalFile = formData.get("original-file-input")
    const originalFileName = originalFile.name;
    const sourceLanguage = formData.get("source-language")
    const targetLanguage = formData.get("target-language")
    const outputPath = formData.get("target-file-input")
    const glossary = formData.get("glossary-select")

    if (originalFile) {
        const reader = new FileReader();

        reader.readAsArrayBuffer(originalFile)
        reader.onload = async function(){
            const fileData = new Uint8Array(reader.result);
            try {
                const result = await invoke('translate_doc_alt', {key: apiKey,
                    fileData: Array.from(fileData),
                    fileName: originalFileName,
                    fileOutput: outputPath,
                    sourceLanguage: sourceLanguage,
                    targetLanguage: targetLanguage,
                    glossaryId: glossary});
                
                const parsedResult = JSON.parse(result);

                if (parsedResult.success) {
                    message("Arquivo traduzido com sucesso!")
                }else{
                    message("Falha na tradução :(")
                }

            } catch (error) {
                console.error('Erro:', error);
                message("Ocorreu um erro!")
            }
        };

    } else {
        console.error("Nenhum arquivo foi selecionado.");
    }
});

cancelarTraducaoBotao.addEventListener("click", (event) =>{
    divConfirmar.classList.remove("show");
} )

targetFileInput.addEventListener("click", async (event) => {
    event.preventDefault();
    const selected = await open({
        directory: true,
        defaultPath: await appDir(),
      });

    try{
        let outputPath = `${selected}/${document.getElementById("target-language").options[document.getElementById("target-language").selectedIndex].innerHTML} - ${document.getElementById("original-file-input").files[0].name}`
        targetFileInput.value = outputPath
    } catch (error) {
        console.error(error)
    }
    
})