const jsonld = require('jsonld');
// var obj = JSON.parse('{"name":"John", "age":30}');
// console.log(obj.name);
// console.log(obj.age);
const doc = {
  "http://schema.org/name": "Manu Sporny",
  "http://schema.org/url": {"@id": "http://manu.sporny.org/"},
  "http://schema.org/image": {"@id": "http://manu.sporny.org/images/manu.png"}
};
const context = {
  "name": "http://schema.org/name",
  "homepage": {"@id": "http://schema.org/url", "@type": "@id"},
  "image": {"@id": "http://schema.org/image", "@type": "@id"}
};
async function compact(){
  const compacted = await jsonld.compact(doc, context);
  console.log(JSON.stringify(compacted, null, 2));
}

compact();