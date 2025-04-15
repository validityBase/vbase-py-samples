module.exports = {
  "overrides": [
    {
      // This fixes Markdown file compatibility with Gitbook.
      // In standard Markdown (e.g., GitHub, most renderers)
      // a single line break is treated as a space.
      // GitBook treats single line breaks as real line breaks.
      "files": ["*.md"],
      "options": {
        "printWidth": 9999,
        "proseWrap": "never"
      }
    }
  ]
};
