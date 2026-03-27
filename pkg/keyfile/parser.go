// abridged from go-nsupdate: https://github.com/n-st/go-nsupdate/blob/master/keyfilereader.go

package keyfile

import (
	"os"
	"regexp"

	"github.com/das-kaesebrot/nsupdate-dyn/pkg/utils"
)

var keyfileKeyBlock =
// ["key", "<key name>", "<key attributes>"]
regexp.MustCompile(`\b(key)\s+"([^"]+)"\s+{([^}]*)};`)

var keyfileAlgorithmLine =
// ["algorithm", "<algorithm name (non-FQDN form)>"]
regexp.MustCompile(`\b(algorithm)\s+"?([^";]+)"?;`)

var keyfileSecretLine =
// ["secret", "<base64-encoded secret>"]
regexp.MustCompile(`\b(secret)\s+"?([^";]+)"?;`)

func ParseTSIGKeyFile(keyfile string) (key *TSIGKey, err error) {
	key = new(TSIGKey)
	data, err := os.ReadFile(keyfile)
	if err != nil {
		return nil, err
	}

	fileContent := string(data)

	keyBlock := keyfileKeyBlock.FindStringSubmatch(fileContent)
	if len(keyBlock) > 0 {
		key.ID = keyBlock[2]
		keyAttributes := keyBlock[3]

		// The file format specification doesn't say what happens if multiple
		// "algorithm" or "secret" attributes are specified. We'll just take
		// the first one in that case.

		algorithmLine := keyfileAlgorithmLine.FindStringSubmatch(keyAttributes)
		if len(algorithmLine) > 0 {
			key.Algorithm = algorithmLine[2]
		}

		secretLine := keyfileSecretLine.FindStringSubmatch(keyAttributes)
		if len(secretLine) > 0 {
			key.Secret = secretLine[2]
		}
	}

	utils.AppendTrailingDotIfNotPresent(&key.ID)
	utils.AppendTrailingDotIfNotPresent(&key.Algorithm)

	return key, nil
}
