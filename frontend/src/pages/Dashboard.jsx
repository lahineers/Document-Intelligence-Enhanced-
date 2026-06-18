import { useEffect, useState } from "react";
import api from "../api/api";

export default function Dashboard() {
  const [file, setFile] = useState(null);
  const [docType, setDocType] = useState("");

  const [documents, setDocuments] = useState([]);

  const [selectedDocuments, setSelectedDocuments] = useState([]);

  const [question, setQuestion] = useState("");
  const [answer, setAnswer] = useState("");

  const loadDocuments = async () => {
    try {
      const res = await api.get("/document");
      setDocuments(res.data);
    } catch (err) {
      console.error(err);
    }
  };

  useEffect(() => {
    loadDocuments();
  }, []);

  const uploadDocument = async () => {
    try {
      const formData = new FormData();

      formData.append("file", file);
      formData.append("doc_type", docType);

      await api.post("/document", formData);

      alert("Upload successful");

      loadDocuments();
    } catch (err) {
      console.error(err);
      alert("Upload failed");
    }
  };

  const askQuestion = async () => {
    try {

        let res;

        if (selectedDocuments.length === 1) {

        res = await api.post("/query", {
            query: question,
            document_id: selectedDocuments[0],
        });

        } else if (selectedDocuments.length >= 2) {

        res = await api.post("/compare", {
            query: question,
            document_ids: selectedDocuments,
        });

        } else {

        alert("Select at least one document");
        return;
        }

        setAnswer(res.data.answer);

    } catch (err) {
        console.error(err);
        alert("Request failed");
    }
    };
  return (
    <div className="p-8 space-y-8">

      <h1 className="text-3xl font-bold">
        DocIntelli Dashboard
      </h1>

      {/* Upload Section */}

      <div className="border p-4 rounded">
        <h2 className="text-xl font-semibold mb-4">
          Upload Document
        </h2>

        <div className="space-y-2">

          <div className="border-2 border-dashed rounded-lg p-10 text-center">
            <input
                type="file"
                onChange={(e) =>
                setFile(e.target.files[0])
                }
            />

            <p className="mt-2">
                Upload a PDF or XLSX file
            </p>

            {file && (
                <p className="mt-2 font-medium">
                Selected: {file.name}
                </p>
            )}
            </div>


          <input
            className="border p-2 w-full"
            placeholder="Document Type"
            value={docType}
            onChange={(e) =>
              setDocType(e.target.value)
            }
          />

          <button
            onClick={uploadDocument}
            className="border px-4 py-2"
          >
            Upload
          </button>

        </div>
      </div>

      {/* Documents */}

      <div className="border p-4 rounded">
        <h2 className="text-xl font-semibold mb-4">
          Documents
        </h2>

        <button
          onClick={loadDocuments}
          className="border px-4 py-2 mb-4"
        >
          Refresh
        </button>

        <div className="max-h-[450px] overflow-y-auto border">
            <table className="w-full border">
            <thead>
                <tr>
                <th>File Name</th>
                <th>Uploaded</th>
                <th>Action</th>
                </tr>
            </thead>

            <tbody>
                {documents.map((doc) => (
                <tr key={doc.doc_id}
                className={
                    selectedDocuments.includes(doc.doc_id)
                    ? "bg-blue-100"
                    : ""
                }>
                    <td>{doc.file_name}</td>
                    <td>{new Date(doc.upload_time).toLocaleDateString("en-GB")}</td>
                    <td>
                        <button
                            onClick={() => {
                                if (selectedDocuments.includes(doc.doc_id)) {
                                setSelectedDocuments(
                                    selectedDocuments.filter(
                                    id => id !== doc.doc_id
                                    )
                                );
                                } else {
                                setSelectedDocuments([
                                    ...selectedDocuments,
                                    doc.doc_id
                                ]);
                                }
                            }}
                            className="border px-2 py-1"
                            >
                            {
                                selectedDocuments.includes(doc.doc_id)
                                ? "Selected"
                                : "Select"
                            }
                            </button>
                    </td>
                </tr>
                ))}
            </tbody>
            </table>
        </div>
      </div>

      {/* Query */}

      <div className="border p-4 rounded">
        <h2 className="text-xl font-semibold mb-4">
          Query Document
        </h2>

       <div className="border p-2 mb-2">
            <strong>Selected Documents:</strong>

            {selectedDocuments.length === 0 ? (
                <p>None Selected</p>
            ) : (
                <ul>
                {documents
                    .filter(doc =>
                    selectedDocuments.includes(
                        doc.doc_id
                    )
                    )
                    .map(doc => (
                    <li key={doc.doc_id}>
                        {doc.file_name}
                    </li>
                    ))}
                </ul>
            )}
        </div>

        <p className="text-sm mb-2">
            {selectedDocuments.length === 1
                ? "Query Mode"
                : selectedDocuments.length > 1
                ? "Comparison Mode"
                : "No Documents Selected"}
        </p>


        <textarea
          className="border p-2 w-full mb-2"
          placeholder="Ask a question..."
          value={question}
          onChange={(e) =>
            setQuestion(e.target.value)
          }
        />

        <button
            onClick={askQuestion}
            disabled={selectedDocuments.length === 0}
            className="border px-4 py-2"
            >
            Ask
        </button>

        <div className="mt-4 border p-4">
          <strong>Answer:</strong>
          <p>{answer}</p>
        </div>
      </div>

    </div>
  );
}