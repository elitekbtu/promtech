const createExpoWebpackConfigAsync = require('@expo/webpack-config');

module.exports = async function (env, argv) {
  const config = await createExpoWebpackConfigAsync(
    {
      ...env,
      babel: {
        dangerouslyAddModulePathsToTranspile: ['react-native-maps'],
      },
    },
    argv
  );

  // Exclude react-native-maps from web builds
  config.resolve.alias['react-native-maps'] = 'react-native-web';

  return config;
};
