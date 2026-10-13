package com.example.ragspringai.ingestion;

import org.springframework.core.io.Resource;
import org.springframework.ai.reader.tika.TikaDocumentReader;
import org.springframework.ai.transformer.splitter.TextSplitter;
import org.springframework.ai.transformer.splitter.TokenTextSplitter;
import org.springframework.ai.vectorstore.VectorStore;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.boot.CommandLineRunner;
import org.springframework.stereotype.Service;

import org.springframework.ai.document.Document;
import java.util.List;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

@Service
public class DocumentIngestionService implements CommandLineRunner  {
    private static final Logger logger = LoggerFactory.getLogger(DocumentIngestionService.class);

    @Value("classpath:/pdf/spring-boot-reference.pdf")
    private Resource pdfResource;
    private final VectorStore vectorStore;

    public DocumentIngestionService(VectorStore vectorStore) {
        this.vectorStore = vectorStore;
    }

    @Override
    public void run(String... args) throws Exception {
        logger.info("DocumentIngestionService called");
        TikaDocumentReader tikaDocumentReader = new TikaDocumentReader(pdfResource);
        TextSplitter textSplitter = TokenTextSplitter.builder().build();
        //List<Document> document = textSplitter.split(tikaDocumentReader.read());
        //vectorStore.accept(document);
        List<Document> chunks = textSplitter.split(tikaDocumentReader.read());
        logger.info("Total chunks: {}", chunks.size());

        for (int i = 0; i < chunks.size(); i += 10) {
            List<Document> batch = chunks.subList(i, Math.min(i + 10, chunks.size()));
            vectorStore.accept(batch);
            logger.info("Stored {}/{}", Math.min(i + 10, chunks.size()), chunks.size());
        }

        logger.info("Ingestion complete");
    }
}
