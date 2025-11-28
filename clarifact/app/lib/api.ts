export async function analyzePost(post: {
  title: string;
  text: string;
  url: string;
  image?: string;
}) {
  const res = await fetch("http://localhost:8000/analyze", {
    method: "POST",
    headers: {
      "Content-Type": "application/json"
    },
    body: JSON.stringify(post)
  });
  return res.json();
}
